#!/usr/bin/env python3
"""
Generate CSV of per-file line counts and how many lines are attributed
to a given author (using `git blame --line-porcelain`).

Usage examples:
  ./blame_author.py --author "gamousquesORT"
  python3 blame_author.py --author "  ./blame_author.py --author "gamousquesORT"
" --ref HEAD

By default the script uses the current branch (`HEAD`) and will try to
use the local git user.name as the default author if available.
"""
import argparse
import os
import re
import shlex
import subprocess
import sys
from typing import List, Tuple


def get_git_username() -> str:
    try:
        res = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True, check=True)
        name = res.stdout.strip()
        return name
    except Exception:
        return "Jorge Silvarredonda"


def list_tracked_files() -> List[str]:
    # Use NUL-separated output to safely handle filenames with newlines
    res = subprocess.run(["git", "ls-files", "-z"], capture_output=True, text=True)
    if res.returncode != 0:
        print("Error: git ls-files failed", file=sys.stderr)
        sys.exit(1)
    data = res.stdout
    if not data:
        return []
    files = data.split('\0')
    # last element after split may be empty
    if files and files[-1] == "":
        files.pop()
    return files


def list_files_from_ref(ref: str) -> List[str]:
    # Use git ls-tree to list files present in the given ref (commit/branch)
    res = subprocess.run(["git", "ls-tree", "-r", "-z", "--name-only", ref], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error: git ls-tree failed for ref '{ref}'", file=sys.stderr)
        sys.exit(1)
    data = res.stdout
    if not data:
        return []
    files = data.split('\0')
    if files and files[-1] == "":
        files.pop()
    return files


def count_lines_from_ref_blob(ref: str, path: str) -> int | None:
    # Return number of lines in the blob from ref:path, or None on error
    try:
        res = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True)
    except Exception:
        return None
    if res.returncode != 0:
        return None
    data = res.stdout
    if not data:
        return 0
    # data is bytes: count newlines and add 1 if doesn't end with newline
    lines = data.count(b"\n")
    if not data.endswith(b"\n"):
        lines += 1
    return lines


def count_file_lines(path: str) -> int:
    # Count lines in binary-safe mode
    try:
        with open(path, "rb") as f:
            data = f.read()
            # number of newline bytes; add 1 if file not empty and doesn't end with newline
            if not data:
                return 0
            lines = data.count(b"\n")
            if not data.endswith(b"\n"):
                lines += 1
            return lines
    except Exception:
        return 0


def blame_author_lines(path: str, ref: str, match_mode) -> int:
    try:
        res = subprocess.run(["git", "blame", "--line-porcelain", ref, "--", path], capture_output=True, text=True)
    except Exception:
        return 0
    if res.returncode != 0:
        # blame failed (binary file, missing file in ref, etc.)
        return 0
    count = 0
    for line in res.stdout.splitlines():
        if line.startswith("author "):
            author = line[len("author "):]
            if match_mode[0] == "regex":
                pattern = match_mode[1]
                if pattern.search(author):
                    count += 1
            else:
                target = match_mode[1]
                if re.sub(r'[^0-9A-Za-z]+', '', author).lower().find(target) != -1:
                    count += 1
    return count


def csv_quote(s: str) -> str:
    # Minimal CSV quoting: wrap in double quotes and escape internal double quotes by doubling
    if '"' in s or ',' in s or '\n' in s:
        return '"' + s.replace('"', '""') + '"'
    return s


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Count per-file lines attributed to an author using git blame")
    parser.add_argument("--author", "-a", default=None, help="Author name (string or regex). If omitted, uses git user.name or a sensible default.")
    parser.add_argument("--ref", "-r", default="HEAD", help="Git ref to blame (default: current branch / HEAD)")
    parser.add_argument("--regex", action="store_true", help="Treat --author as a regular expression")
    parser.add_argument("--ignore-case", action="store_true", help="Perform case-insensitive matching")
    parser.add_argument("--normalize", action="store_true", help="Normalize author strings (remove non-alphanumerics) before matching")
    parser.add_argument("--show-zero", action="store_true", help="Include files with zero total lines in output")
    parser.add_argument("--limit", type=int, default=0, help="Limit output to top N results (after sorting); 0 means no limit")
    parser.add_argument("--files-from-ref", action="store_true", help="List files from the given ref (branch/commit) instead of working-tree tracked files")
    args = parser.parse_args(argv)

    author = args.author if args.author is not None else get_git_username()

    def normalize_str(s: str) -> str:
        return re.sub(r'[^0-9A-Za-z]+', '', s).lower()

    # Build matching mode: either ('regex', compiled_pattern) or ('normalize', normalized_string)
    match_mode = None
    if args.regex:
        flags = re.IGNORECASE if args.ignore_case else 0
        pattern = re.compile(author, flags)
        match_mode = ("regex", pattern)
    else:
        if args.normalize:
            match_mode = ("normalize", normalize_str(author))
        else:
            if args.ignore_case:
                pattern = re.compile(re.escape(author), re.IGNORECASE)
            else:
                pattern = re.compile(re.escape(author))
            match_mode = ("regex", pattern)

    if args.files_from_ref:
        files = list_files_from_ref(args.ref)
    else:
        files = list_tracked_files()
    results: List[Tuple[str, int, int, float]] = []

    for file in files:
        # If files were obtained from ref, the file may not exist in working tree;
        # use the blob content from the ref to count lines. Otherwise count
        # lines from the working-tree file.
        if args.files_from_ref:
            total_lines = count_lines_from_ref_blob(args.ref, file)
            if total_lines is None:
                # couldn't read blob (e.g. submodule or binary); skip
                continue
        else:
            # skip directories (shouldn't appear from git ls-files) and submodules
            if not os.path.isfile(file):
                continue
            total_lines = count_file_lines(file)
        if total_lines == 0 and not args.show_zero:
            continue
        jorge_lines = blame_author_lines(file, args.ref, match_mode)
        pct = (jorge_lines / total_lines * 100) if total_lines > 0 else 0.0
        results.append((file, jorge_lines, total_lines, pct))

    # sort by jorge_lines desc
    results.sort(key=lambda r: r[1], reverse=True)

    # print metadata header (CSV comment) and CSV header with descriptive column names
    # leading '#' marks the metadata line as a comment for CSV viewers
    print(f"# generated_by=blame_author.py author={author} ref={args.ref}")
    print("file_path,lines_by_author,total_lines_in_file,percent_lines_by_author")
    limit = args.limit if args.limit > 0 else None
    for i, (file, a_lines, t_lines, pct) in enumerate(results):
        if limit is not None and i >= limit:
            break
        print(f"{csv_quote(file)},{a_lines},{t_lines},{pct:.2f}%")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
