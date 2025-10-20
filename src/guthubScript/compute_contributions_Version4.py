#!/usr/bin/env python3
"""
compute_contributions.py

Usage:
  python3 compute_contributions.py --path NearDupFinder
  python3 compute_contributions.py --path NearDupFinder --weights 0.3 0.5 0.2
  python3 compute_contributions.py --path NearDupFinder --extensions .cs,.csproj,.json,.css,.map,.razor,.razor.css

What this updated script does:
 - Computes per-author metrics (distinct files touched, current lines owned via git blame, commits touching the path)
 - Filters file lists and blame to only consider files with the provided extensions (default: .cs, .csproj, .json, .css, .map, .razor, .razor.css)
 - Outputs a ranked table and (by default) a detailed list of files touched per author limited to the chosen extensions.

Notes:
 - Run this from the repository root (where .git exists).
 - Requires git installed and available on PATH.
"""
import argparse
import subprocess
from collections import defaultdict, Counter
import sys
import os

def run(cmd, cwd=None):
    return subprocess.check_output(cmd, stderr=subprocess.DEVNULL, cwd=cwd).decode(errors='replace')

def commit_counts(path):
    out = run(["git", "log", "--no-merges", "--pretty=%an", "--", path])
    return Counter([l.strip() for l in out.splitlines() if l.strip()])


def days_worked_per_author(path):
    """
    Count distinct calendar days (YYYY-MM-DD) on which each author made at least one commit
    that touches the given path. Uses git log --date=short to get commit dates.
    """
    files_by_day = defaultdict(set)
    git_cmd = ["git", "log", "--no-merges", "--pretty=format:%an%x09%ad", "--date=short", "--", path]
    try:
        out = run(git_cmd)
    except subprocess.CalledProcessError:
        return Counter()
    days_by_author = defaultdict(set)
    for line in out.splitlines():
        if not line.strip():
            continue
        # each line is: Author<TAB>YYYY-MM-DD
        parts = line.split('\t')
        if len(parts) >= 2:
            author = parts[0].strip()
            date = parts[1].strip()
            if author and date:
                days_by_author[author].add(date)
    return Counter({a: len(dates) for a, dates in days_by_author.items()})

def _matches_ext(filename, exts):
    # Normalize and check if filename ends with any of the provided extensions.
    # Ensure longer extensions (e.g. .razor.css) are correctly matched by checking all.
    fn = filename.lower()
    for e in exts:
        if fn.endswith(e):
            return True
    return False

def files_touched_per_author(path, exts):
    """
    Collect distinct filenames touched per author restricted to the specified extensions.
    Uses a clear separator in --pretty=format to reliably parse authors.
    """
    files_by_author = defaultdict(set)
    git_cmd = ["git", "log", "--no-merges", "--pretty=format:--AUTHOR--%an", "--name-only", "--", path]
    try:
        out = run(git_cmd)
    except subprocess.CalledProcessError:
        return files_by_author
    current_author = None
    for line in out.splitlines():
        if not line:
            continue
        if line.startswith("--AUTHOR--"):
            current_author = line[len("--AUTHOR--"):].strip()
            continue
        # line is a file path, add to current author set if it matches extension
        if current_author and _matches_ext(line, exts):
            files_by_author[current_author].add(line.strip())
    return files_by_author

def lines_owned_per_author(path, exts, skip_patterns=None):
    """
    For each tracked file under path, run git blame and count 'author' occurrences,
    only for files matching the provided extensions.
    skip_patterns: list of path substrings to skip (like bin/, obj/)
    """
    if skip_patterns is None:
        skip_patterns = ['bin/', 'obj/']
    # list files under path tracked by git
    try:
        files = run(["git", "ls-files", path]).splitlines()
    except subprocess.CalledProcessError:
        return Counter()
    counts = Counter()
    for f in files:
        if not f.strip():
            continue
        if any(p in f for p in skip_patterns):
            continue
        if not _matches_ext(f, exts):
            continue
        # ensure file exists in working tree (ls-files can list deleted files in some edge cases)
        if not os.path.exists(f):
            continue
        try:
            blame = run(["git", "blame", "-w", "-e", "--line-porcelain", f])
        except subprocess.CalledProcessError:
            # skip files we can't blame (binary or removed)
            continue
        for bl in blame.splitlines():
            if bl.startswith("author "):
                author = bl[len("author "):].strip()
                counts[author] += 1
    return counts

def normalize(d):
    if not d:
        return {}
    m = max(d.values())
    if m == 0:
        return {k: 0.0 for k in d}
    return {k: v / m for k, v in d.items()}

def pretty_print_results(results, files_by_author, show_files):
    print()
    print("{:30} {:>6} {:>8} {:>8} {:>6}   {:>6} {:>6} {:>6} {:>6}   {:>7}".format(
        "Author","Files","Lines","Commits","Days","f_norm","l_norm","c_norm","d_norm","Score"))
    for r in results:
        print("{:30} {:6d} {:8d} {:8d} {:6d}   {:6.3f} {:6.3f} {:6.3f} {:6.3f}   {:7.4f}".format(
            r["author"], r["files"], r["lines"], r["commits"], r.get("days", 0),
            r["files_norm"], r["lines_norm"], r["commits_norm"], r.get("days_norm", 0.0), r["score"]))
    if show_files:
        print("\nDetailed files touched per author (filtered by extensions):")
        for r in results:
            author = r["author"]
            fls = sorted(files_by_author.get(author, []))
            print("\n--- {} ({} files) ---".format(author, len(fls)))
            if fls:
                for f in fls:
                    print(f)
            else:
                print("(no files recorded)")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--path", required=True, help="Path to folder to analyze (e.g. NearDupFinder)")
    p.add_argument("--weights", nargs=3, type=float, default=[0.3, 0.5, 0.2],
                   help="Weights: files_touched lines_owned commits (must sum to >0). Default 0.3 0.5 0.2")
    p.add_argument("--extensions", type=str,
                   default=" .cs,.csproj,.json,.css,.map,.razor,.razor.css",
                   help="Comma-separated list of file extensions to consider (e.g. .cs,.json). Default includes .cs .csproj .json .css .map .razor .razor.css")
    p.add_argument("--output-files-per-author", action="store_true",
                   help="Also output the list of distinct files touched by each author (default: True)")
    p.add_argument("--no-output-files-per-author", dest="output_files_per_author", action="store_false",
                   help="Do not output per-author file lists")
    p.set_defaults(output_files_per_author=True)
    args = p.parse_args()

    path = args.path
    w_files, w_lines, w_commits = args.weights
    total_w = w_files + w_lines + w_commits
    if total_w <= 0:
        print("Weights must sum to > 0", file=sys.stderr); sys.exit(1)
    # normalize weights to sum 1
    w_files /= total_w; w_lines /= total_w; w_commits /= total_w

    # Build extension list: normalize to lowercase and ensure leading dot
    exts_raw = [e.strip() for e in args.extensions.split(",") if e.strip()]
    exts = []
    for e in exts_raw:
        ee = e.lower()
        if not ee.startswith("."):
            ee = "." + ee
        exts.append(ee)

    # Validate git repo and path
    try:
        _ = run(["git", "rev-parse", "--is-inside-work-tree"])
    except subprocess.CalledProcessError:
        print("Not a git repository (or git not available). Run this inside a git repo.", file=sys.stderr)
        sys.exit(1)

    # Gather raw metrics (filtered by extensions where applicable)
    commits = commit_counts(path)
    files_by_author = files_touched_per_author(path, exts)
    lines_owned = lines_owned_per_author(path, exts)
    days_worked = days_worked_per_author(path)

    # ensure all authors present in metrics (union)
    all_authors = set(commits.keys()) | set(files_by_author.keys()) | set(lines_owned.keys())

    files_count = {a: len(files_by_author.get(a, set())) for a in all_authors}
    commits_count = {a: commits.get(a, 0) for a in all_authors}
    lines_count = {a: lines_owned.get(a, 0) for a in all_authors}
    days_count = {a: days_worked.get(a, 0) for a in all_authors}

    files_norm = normalize(files_count)
    lines_norm = normalize(lines_count)
    commits_norm = normalize(commits_count)
    days_norm = normalize(days_count)

    results = []
    for a in sorted(all_authors):
        score = (w_files * files_norm.get(a,0.0) +
                 w_lines * lines_norm.get(a,0.0) +
                 w_commits * commits_norm.get(a,0.0))
        results.append({
            "author": a,
            "files": files_count.get(a,0),
            "lines": lines_count.get(a,0),
            "commits": commits_count.get(a,0),
            "days": days_count.get(a,0),
            "files_norm": round(files_norm.get(a,0.0),3),
            "lines_norm": round(lines_norm.get(a,0.0),3),
            "commits_norm": round(commits_norm.get(a,0.0),3),
            "days_norm": round(days_norm.get(a,0.0),3),
            "score": round(score,4)
        })

    # sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)

    print("Computed contribution ranking for path:", path)
    print(f"Extensions considered: {', '.join(exts)}")
    print(f"Weights (files, lines, commits): {w_files:.3f}, {w_lines:.3f}, {w_commits:.3f}")
    pretty_print_results(results, files_by_author, args.output_files_per_author)