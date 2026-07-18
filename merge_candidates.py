"""Fallback merge step: when discover.py reports SEARXNG_RATE_LIMITED (see
data/stalled_queries_<slug>.json), a Claude session runs the stalled queries
through its own WebSearch tool instead, then feeds the results through this
script in the same candidate schema discover.py produces, so they land in the
same data/candidates_<slug>.json used by verify.py / classify_category.py.

    python merge_candidates.py <region_slug> <path-to-new-candidates.json>

<path-to-new-candidates.json> is a JSON list of objects shaped like:
    {"platform": "tiktok", "handle": "somehandle" | null, "name": "...",
     "source_url": "...", "discovery_snippet": "..."}
"""
import json
import sys


def merge(region_slug: str, new_candidates_path: str) -> int:
    existing_path = f"data/candidates_{region_slug}.json"
    try:
        with open(existing_path, encoding="utf-8") as f:
            existing = json.load(f)
    except FileNotFoundError:
        existing = []

    with open(new_candidates_path, encoding="utf-8") as f:
        incoming = json.load(f)

    seen = {(c["platform"], c.get("handle") or c["source_url"]) for c in existing}
    added = 0
    for c in incoming:
        key = (c["platform"], c.get("handle") or c["source_url"])
        if key not in seen:
            existing.append(c)
            seen.add(key)
            added += 1

    with open(existing_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)
    return added


if __name__ == "__main__":
    slug = sys.argv[1]
    new_path = sys.argv[2]
    n = merge(slug, new_path)
    print(f"merged {n} new candidates -> data/candidates_{slug}.json")
