"""Stage 1: find candidate creators for a region across all platforms.

    python discover.py <region_slug>

Writes data/candidates_<region_slug>.json. Pure SearXNG, no Claude session.
"""
import json
import os
import re
import sys

from regions import DISCOVERY_QUERY_TEMPLATES, PLATFORMS, REGIONS
from searxng_client import RateLimited, search

HANDLE_RE = re.compile(r"@([A-Za-z0-9_.]{2,30})")

# Profile-URL handle patterns per platform. Search result titles are often a
# video/article headline ("RANTS FROM THE SHOWER") rather than the creator's
# actual name, so pulling the handle straight out of the profile URL is a much
# more reliable "who is this" signal than the title text.
URL_HANDLE_PATTERNS = {
    "tiktok": re.compile(r"tiktok\.com/@([A-Za-z0-9_.]{2,30})"),
    "instagram": re.compile(r"instagram\.com/([A-Za-z0-9_.]{2,30})/?(?:$|\?)"),
    "twitter": re.compile(r"(?:twitter|x)\.com/@?([A-Za-z0-9_]{2,30})/?(?:$|\?|/status)"),
    "facebook": re.compile(r"facebook\.com/(?!groups/|p/|posts/|watch/)([A-Za-z0-9_.]{2,30})/?(?:$|\?|/about)"),
    "youtube": re.compile(r"youtube\.com/(?:@|c/|user/)([A-Za-z0-9_.-]{2,40})/?(?:$|\?)"),
}


def extract_handle(platform: str, title: str, content: str, url: str) -> str | None:
    handle_match = HANDLE_RE.search(title + " " + content)
    if handle_match:
        return handle_match.group(1)
    url_pattern = URL_HANDLE_PATTERNS.get(platform)
    if url_pattern:
        url_match = url_pattern.search(url)
        if url_match:
            return url_match.group(1)
    return None


def discover(region_slug: str) -> tuple[list[dict], list[tuple[str, str]]]:
    """Returns (candidates, stalled_queries). stalled_queries is the list of
    (platform, query) pairs that hit RateLimited — the caller (or a Claude
    session orchestrating this pipeline) should re-run those via WebSearch and
    merge the results in with merge_candidates.py rather than treat them as
    "no matches found"."""
    region = REGIONS[region_slug]
    candidates = {}
    stalled = []
    for platform in PLATFORMS:
        for template in DISCOVERY_QUERY_TEMPLATES[platform]:
            for term in region["search_terms"][:2]:
                query = template.format(region=term)
                try:
                    results = search(query)
                except RateLimited:
                    stalled.append((platform, query))
                    continue
                for r in results:
                    handle = extract_handle(platform, r["title"], r["content"], r["url"])
                    key = (platform, handle or r["url"])
                    if key not in candidates:
                        candidates[key] = {
                            "platform": platform,
                            "handle": handle,
                            "name": r["title"].split("(")[0].split("|")[0].strip(),
                            "source_url": r["url"],
                            "discovery_snippet": r["content"],
                        }
    return list(candidates.values()), stalled


if __name__ == "__main__":
    slug = sys.argv[1] if len(sys.argv) > 1 else "ohio"
    os.makedirs("data", exist_ok=True)
    out, stalled = discover(slug)
    with open(f"data/candidates_{slug}.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"{len(out)} candidates -> data/candidates_{slug}.json")
    if stalled:
        with open(f"data/stalled_queries_{slug}.json", "w", encoding="utf-8") as f:
            json.dump([{"platform": p, "query": q} for p, q in stalled], f, indent=2)
        print(f"SEARXNG_RATE_LIMITED: {len(stalled)} queries need a WebSearch fallback "
              f"-> data/stalled_queries_{slug}.json (run merge_candidates.py after)")
