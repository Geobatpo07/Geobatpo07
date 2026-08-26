#!/usr/bin/env python3
"""Sync live GitHub star counts into the README.md star markers.

Only stdlib is used (urllib, re, json) so this runs with no extra
dependencies in CI. For each public repo listed below, it fetches the
current star count from the GitHub API and rewrites the matching
<!--STARS:repo-->N<!--/STARS--> marker in README.md, only touching the
file if a value actually changed.
"""

import json
import re
import sys
import urllib.error
import urllib.request

OWNER = "Geobatpo07"
REPOS = [
    "datahut-duckhouse",
    "scientific-assistant",
    "simulation-chlordecone",
]
README_PATH = "README.md"
API_URL = "https://api.github.com/repos/{owner}/{repo}"


def fetch_stars(owner, repo):
    url = API_URL.format(owner=owner, repo=repo)
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"{owner}-profile-star-sync",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.load(response)
            return data.get("stargazers_count")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        print(f"warning: could not fetch stars for {repo}: {exc}", file=sys.stderr)
        return None


def main():
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    for repo in REPOS:
        stars = fetch_stars(OWNER, repo)
        if stars is None:
            continue

        pattern = re.compile(rf"<!--STARS:{re.escape(repo)}-->\d+<!--/STARS-->")
        if not pattern.search(content):
            print(f"warning: no marker found for {repo}", file=sys.stderr)
            continue

        replacement = f"<!--STARS:{repo}-->{stars}<!--/STARS-->"
        content = pattern.sub(replacement, content)

    if content != original_content:
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        print("README.md updated with new star counts.")
    else:
        print("No changes: star counts already up to date.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
