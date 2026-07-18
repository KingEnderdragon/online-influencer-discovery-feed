"""Fast path for the WebSearch fallback: when SearXNG is rate-limited (see
discover.py's SEARXNG_RATE_LIMITED signal), a Claude session runs the stalled
queries through WebSearch instead. This script takes those results straight
through to the feed — no second SearXNG residency search (that's what pulled
in wrong-person matches before), just one Ollama pass to judge residency from
the WebSearch snippet itself and one to classify category — then merges into
candidates/verified/categorized, deduped by name.

    python ingest_websearch.py <region_slug> <path-to-new-candidates.json>

<path-to-new-candidates.json> is a JSON list shaped like:
    {"platform": "tiktok", "handle": "somehandle" | null, "name": "...",
     "source_url": "...", "discovery_snippet": "..."}
"""
import json
import sys

from ollama_client import classify_category, judge_residency
from regions import REGIONS


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def dedupe_by_name(entries: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for e in entries:
        key = e["name"].strip().lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(e)
    return out


def ingest(region_slug: str, new_candidates_path: str) -> int:
    region = REGIONS[region_slug]
    with open(new_candidates_path, encoding="utf-8") as f:
        incoming = json.load(f)

    candidates = load(f"data/candidates_{region_slug}.json")
    verified = load(f"data/verified_{region_slug}.json")
    categorized = load(f"data/categorized_{region_slug}.json")

    existing_names = {c["name"].strip().lower() for c in candidates}
    added = 0
    for c in incoming:
        if c["name"].strip().lower() in existing_names:
            continue
        existing_names.add(c["name"].strip().lower())

        residency = judge_residency(
            c["name"], region["name"],
            [{"title": c["name"], "content": c.get("discovery_snippet", ""), "url": c["source_url"]}],
        )
        category = classify_category(c["name"], c["platform"], c.get("discovery_snippet", ""))

        candidates.append(c)
        verified.append({**c, **residency})
        categorized.append({**c, **residency, **category})
        added += 1

    candidates = dedupe_by_name(candidates)
    verified = dedupe_by_name(verified)
    categorized = dedupe_by_name(categorized)

    json.dump(candidates, open(f"data/candidates_{region_slug}.json", "w", encoding="utf-8"), indent=2)
    json.dump(verified, open(f"data/verified_{region_slug}.json", "w", encoding="utf-8"), indent=2)
    json.dump(categorized, open(f"data/categorized_{region_slug}.json", "w", encoding="utf-8"), indent=2)
    return added


if __name__ == "__main__":
    slug = sys.argv[1]
    new_path = sys.argv[2]
    n = ingest(slug, new_path)
    print(f"ingested {n} new candidates -> candidates/verified/categorized_{slug}.json (deduped by name)")
