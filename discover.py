"""Stage 1: find candidate creators for a region across all platforms.

    python discover.py <region_slug>

Writes data/candidates_<region_slug>.json. Pure SearXNG, no Claude session.
"""
import json
import os
import re
import sys

from regions import DISCOVERY_QUERY_TEMPLATES, PLATFORMS, REGIONS
from searxng_client import search

HANDLE_RE = re.compile(r"@([A-Za-z0-9_.]{2,30})")


def discover(region_slug: str) -> list[dict]:
    region = REGIONS[region_slug]
    candidates = {}
    for platform in PLATFORMS:
        for template in DISCOVERY_QUERY_TEMPLATES[platform]:
            for term in region["search_terms"][:2]:
                results = search(template.format(region=term))
                for r in results:
                    handle_match = HANDLE_RE.search(r["title"] + " " + r["content"])
                    handle = handle_match.group(1) if handle_match else None
                    key = (platform, handle or r["url"])
                    if key not in candidates:
                        candidates[key] = {
                            "platform": platform,
                            "handle": handle,
                            "name": r["title"].split("(")[0].split("|")[0].strip(),
                            "source_url": r["url"],
                            "discovery_snippet": r["content"],
                        }
    return list(candidates.values())


if __name__ == "__main__":
    slug = sys.argv[1] if len(sys.argv) > 1 else "ohio"
    os.makedirs("data", exist_ok=True)
    out = discover(slug)
    with open(f"data/candidates_{slug}.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"{len(out)} candidates -> data/candidates_{slug}.json")
