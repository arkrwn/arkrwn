#!/usr/bin/env python3
"""Generate assets/stats.svg for the profile README.

Numbers come straight from the GitHub GraphQL API (no third-party service):
all-time contributions, last-12-month contributions, current and longest
streak, and public repo count. Run by .github/workflows/stats.yml.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys

USER = "arkrwn"
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "stats.svg")


def gql(query: str) -> dict:
    out = subprocess.run(["gh", "api", "graphql", "-f", f"query={query}"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"graphql failed: {out.stderr.strip()[:300]}")
    return json.loads(out.stdout)


def contributions(year_from: int, year_to: int) -> int:
    q = (f'query {{ user(login:"{USER}") {{ contributionsCollection('
         f'from:"{year_from}-01-01T00:00:00Z", to:"{year_to}-12-31T23:59:59Z") '
         f'{{ contributionCalendar {{ totalContributions }} }} }} }}')
    return gql(q)["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]


def main() -> None:
    today = dt.date.today()
    start_year = 2016
    total_all = sum(contributions(y, y) for y in range(start_year, today.year + 1))

    q = (f'query {{ user(login:"{USER}") {{ contributionsCollection {{ contributionCalendar '
         f'{{ weeks {{ contributionDays {{ date contributionCount }} }} }} }} }} }}')
    weeks = gql(q)["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    days = [(dt.date.fromisoformat(d["date"]), d["contributionCount"])
            for w in weeks for d in w["contributionDays"]]
    total_year = sum(c for _, c in days)

    longest = run = 0
    for _, c in days:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)

    current = 0
    for i, (d, c) in enumerate(reversed(days)):
        if c > 0:
            current += 1
        elif i == 0:          # hari ini belum ada kontribusi: hitung dari kemarin
            continue
        else:
            break

    # REST: jumlah repo publik yang sebenarnya (GraphQL privacy filter butuh scope user)
    out = subprocess.run(["gh", "api", f"users/{USER}", "--jq", ".public_repos"],
                         capture_output=True, text=True, check=True)
    public_repos = int(out.stdout.strip())

    def block(x: int, label: str, value: str, note: str, accent: str) -> str:
        return f'''  <g>
    <text x="{x}" y="82" font-family="Inter, 'Segoe UI', Arial, sans-serif" font-size="12"
          font-weight="700" letter-spacing="1.6" fill="#7E93B5">{label}</text>
    <text x="{x}" y="136" font-family="Inter, 'Segoe UI', Arial, sans-serif" font-size="46"
          font-weight="800" fill="{accent}">{value}</text>
    <text x="{x}" y="162" font-family="Inter, 'Segoe UI', Arial, sans-serif" font-size="12"
          fill="#6F87AC">{note}</text>
  </g>'''

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="210" viewBox="0 0 1200 210" role="img" aria-label="GitHub stats">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0B1020"/>
      <stop offset="55%" stop-color="#131A33"/>
      <stop offset="100%" stop-color="#0E2430"/>
    </linearGradient>
    <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#5B8CFF" stop-opacity="0.55"/>
      <stop offset="100%" stop-color="#38E1C6" stop-opacity="0.35"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="210" rx="24" fill="url(#bg)"/>
  <rect x="1" y="1" width="1198" height="208" rx="23" fill="none" stroke="url(#edge)"/>
{block(48, "TOTAL CONTRIBUTIONS", f"{total_all:,}".replace(",", "."), f"since {start_year}", "#EAF1FF")}
{block(330, "LAST 12 MONTHS", str(total_year), "rolling year", "#A9C4FF")}
{block(586, "LONGEST STREAK", f"{longest} d", "consecutive days", "#38E1C6")}
{block(842, "CURRENT STREAK", f"{current} d", "as of today", "#6FE7D2")}
  <g>
    <text x="48" y="190" font-family="Inter, 'Segoe UI', Arial, sans-serif" font-size="11"
          fill="#5C708F">public repos: {public_repos} · updated {today.isoformat()} · generated from the GitHub API</text>
  </g>
</svg>
'''
    os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
    with open(OUT, "w") as fh:
        fh.write(svg)
    print(f"wrote {OUT}: total={total_all} year={total_year} longest={longest} current={current} repos={public_repos}")


if __name__ == "__main__":
    main()
