"""Stage 2.5: classify each verified candidate's content category, so the feed
can filter down to career/job-focused creators only (per user request: exclude
food, vlog, and lifestyle creators; keep people who blog about their jobs).

    python classify_category.py <region_slug>

Reads data/verified_<region_slug>.json, writes data/categorized_<region_slug>.json
with a 'category' field per candidate ("occupational" | "food" | "lifestyle" | "other").
Local Ollama only, no Claude session needed.
"""
import json
import sys

from ollama_client import classify_category


def categorize(region_slug: str) -> list[dict]:
    with open(f"data/verified_{region_slug}.json", encoding="utf-8") as f:
        candidates = json.load(f)

    out = []
    for c in candidates:
        judgment = classify_category(c["name"], c["platform"], c.get("discovery_snippet", ""))
        out.append({**c, **judgment})
    return out


if __name__ == "__main__":
    slug = sys.argv[1] if len(sys.argv) > 1 else "ohio"
    out = categorize(slug)
    with open(f"data/categorized_{slug}.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    counts = {}
    for c in out:
        counts[c["category"]] = counts.get(c["category"], 0) + 1
    print(f"{slug}: {counts} -> data/categorized_{slug}.json")
