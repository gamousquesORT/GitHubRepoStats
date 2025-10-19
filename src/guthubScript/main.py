#!/usr/bin/env python3
"""
compute_contributions.py

Usage:
  python3 compute_contributions.py --path NearDupFinder
  python3 compute_contributions.py --path NearDupFinder --weights 0.3 0.5 0.2

Output:
  - For each author: files_touched, lines_owned, commits, normalized metrics, combined score
"""
import argparse
import subprocess
from collections import defaultdict, Counter
import sys

def run(cmd):
    return subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode(errors='replace')

def authors_from_log(path):
    out = run(["git", "log", "--no-merges", "--pretty=%an", "--", path])
    authors = [l.strip() for l in out.splitlines() if l.strip()]
    return list(dict.fromkeys(authors))  # preserve order, unique

def commit_counts(path):
    out = run(["git", "log", "--no-merges", "--pretty=%an", "--", path])
    return Counter([l.strip() for l in out.splitlines() if l.strip()])

def files_touched_per_author(path):
    out = run(["git", "log", "--no-merges", "--pretty=%an", "--name-only", "--", path])
    files_by_author = defaultdict(set)
    current_author = None
    for line in out.splitlines():
        line = line.rstrip()
        if not line:
            continue
        # If line looks like an author name vs a filename: authors usually have spaces; filenames contain /
        # But the git format places author lines where they were produced by --pretty, so detect that:
        # Heuristic: if line does NOT contain a slash and not ending with typical extension? Safer: treat lines matching an author from commit list
        if line in authors_cache:
            current_author = line
            continue
        if current_author:
            files_by_author[current_author].add(line)
    return files_by_author

def lines_owned_per_author(path):
    files = run(["git", "ls-files", path]).splitlines()
    counts = Counter()
    for f in files:
        if not f.strip():
            continue
        # Skip empty files gracefully
        try:
            blame = run(["git", "blame", "-w", "-e", "--line-porcelain", f])
        except subprocess.CalledProcessError:
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

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--path", required=True, help="Path to folder to analyze (e.g. NearDupFinder)")
    p.add_argument("--weights", nargs=3, type=float, default=[0.3, 0.5, 0.2],
                   help="Weights: files_touched lines_owned commits (must sum to >0). Default 0.3 0.5 0.2")
    args = p.parse_args()

    path = args.path
    w_files, w_lines, w_commits = args.weights
    total_w = w_files + w_lines + w_commits
    if total_w <= 0:
        print("Weights must sum to > 0", file=sys.stderr); sys.exit(1)
    # normalize weights to sum 1
    w_files /= total_w; w_lines /= total_w; w_commits /= total_w

    # Gather authors from log under path
    try:
        authors = authors_from_log(path)
    except subprocess.CalledProcessError:
        print("git command failed. Run this inside a git repo and ensure the path exists.", file=sys.stderr)
        sys.exit(1)
    if not authors:
        print("No commits found in path:", path)
        sys.exit(0)

    # cache authors for file parsing heuristic
    authors_cache = set(authors)

    commits = commit_counts(path)
    files_by_author = files_touched_per_author(path)
    lines_owned = lines_owned_per_author(path)

    # ensure all authors present in metrics
    all_authors = set(authors) | set(commits.keys()) | set(files_by_author.keys()) | set(lines_owned.keys())

    files_count = {a: len(files_by_author.get(a, set())) for a in all_authors}
    commits_count = {a: commits.get(a, 0) for a in all_authors}
    lines_count = {a: lines_owned.get(a, 0) for a in all_authors}

    files_norm = normalize(files_count)
    lines_norm = normalize(lines_count)
    commits_norm = normalize(commits_count)

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
            "files_norm": round(files_norm.get(a,0.0),3),
            "lines_norm": round(lines_norm.get(a,0.0),3),
            "commits_norm": round(commits_norm.get(a,0.0),3),
            "score": round(score,4)
        })

    # sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)

    print("Computed contribution ranking for path:", path)
    print(f"Weights (files, lines, commits): {w_files:.3f}, {w_lines:.3f}, {w_commits:.3f}")
    print()
    print("{:30} {:>6} {:>8} {:>8}   {:>6} {:>6} {:>6}   {:>7}".format(
        "Author","Files","Lines","Commits","f_norm","l_norm","c_norm","Score"))
    for r in results:
        print("{:30} {:6d} {:8d} {:8d}   {:6.3f} {:6.3f} {:6.3f}   {:7.4f}".format(
            r["author"], r["files"], r["lines"], r["commits"],
            r["files_norm"], r["lines_norm"], r["commits_norm"], r["score"]))