"""Merge results from a manual tinyfish pass back into the pipeline data.

    python ingest_tinyfish.py <region>

Reads data/tinyfish_results_<region>.json (a Claude session's output, written
per the instructions in request_tinyfish.py's manifest — a JSON list of
{name, platform, handle, confidence, quote, source_url}) and merges it into
data/candidates_<region>.json and data/verified_<region>.json, deduping by
(platform, handle or name). Run generate_static_page.py again afterward.
"""
import json
import sys


def merge(region_slug: str) -> None:
    with open(f"data/tinyfish_results_{region_slug}.json", encoding="utf-8") as f:
        new_entries = json.load(f)

    for name, wanted_keys in (
        (f"data/candidates_{region_slug}.json", ("platform", "handle", "name", "source_url", "discovery_snippet")),
        (f"data/verified_{region_slug}.json", ("platform", "handle", "name", "source_url", "discovery_snippet", "confidence", "quote")),
    ):
        try:
            with open(name, encoding="utf-8") as f:
                existing = json.load(f)
        except FileNotFoundError:
            existing = []

        seen = {(e["platform"], e.get("handle") or e["name"]) for e in existing}
        added = 0
        for e in new_entries:
            key = (e["platform"], e.get("handle") or e["name"])
            if key in seen:
                continue
            seen.add(key)
            existing.append({k: e.get(k, "") for k in wanted_keys})
            added += 1

        with open(name, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)
        print(f"{added} new entr{'y' if added == 1 else 'ies'} -> {name}")


if __name__ == "__main__":
    slug = sys.argv[1] if len(sys.argv) > 1 else "ohio"
    merge(slug)
