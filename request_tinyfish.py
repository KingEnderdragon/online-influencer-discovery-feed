"""Optional, on-demand ask: compile a manifest of gaps for a broader tinyfish
pass, for when SearXNG + normal search plainly aren't covering something
(thin platform, or a name with unresolved residency).

    python request_tinyfish.py <region> [--min-per-platform N]

Writes data/tinyfish_requests_<region>.json. This does NOT call tinyfish
itself (it has no standalone API outside a Claude session's MCP tools) — it
just hands a Claude session a concrete, bounded list of what to go dig up,
instead of "re-research the whole region." Run it whenever you want that
broader pass, not automatically as part of discover.py/verify.py.
"""
import argparse
import json
import os

from regions import PLATFORMS, REGIONS


def build_manifest(region_slug: str, min_per_platform: int) -> dict:
    region = REGIONS[region_slug]

    candidates = []
    cand_path = f"data/candidates_{region_slug}.json"
    if os.path.exists(cand_path):
        with open(cand_path, encoding="utf-8") as f:
            candidates = json.load(f)

    verified = []
    ver_path = f"data/verified_{region_slug}.json"
    if os.path.exists(ver_path):
        with open(ver_path, encoding="utf-8") as f:
            verified = json.load(f)

    counts = {p: 0 for p in PLATFORMS}
    for c in candidates:
        counts[c["platform"]] = counts.get(c["platform"], 0) + 1

    thin_platforms = [p for p, n in counts.items() if n < min_per_platform]
    unresolved = [
        {"name": v["name"], "platform": v["platform"], "handle": v.get("handle"), "source_url": v["source_url"]}
        for v in verified
        if v["confidence"] == "none"
    ]

    return {
        "region": region["name"],
        "region_slug": region_slug,
        "thin_platforms": [
            {
                "platform": p,
                "candidate_count": counts[p],
                "ask": f"Find {min_per_platform - counts[p]}+ more real {p} creators genuinely "
                       f"resident in {region['name']} — SearXNG only turned up {counts[p]}.",
            }
            for p in thin_platforms
        ],
        "unresolved_candidates": unresolved,
        "instructions": (
            "Hand this file to a Claude session with tinyfish/searxng-MCP access. For "
            "thin_platforms, do broader discovery on that platform+region. For "
            "unresolved_candidates, try to confirm or rule out current residency. "
            "Write findings as a JSON list of {name, platform, handle, confidence, quote, "
            "source_url} to data/tinyfish_results_<region>.json, then run "
            "`python ingest_tinyfish.py <region>` to merge them in."
        ),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("region")
    parser.add_argument("--min-per-platform", type=int, default=5)
    args = parser.parse_args()

    manifest = build_manifest(args.region, args.min_per_platform)
    os.makedirs("data", exist_ok=True)
    out_path = f"data/tinyfish_requests_{args.region}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    thin = len(manifest["thin_platforms"])
    unresolved = len(manifest["unresolved_candidates"])
    print(f"{thin} thin platform(s), {unresolved} unresolved candidate(s) -> {out_path}")
