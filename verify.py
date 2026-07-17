"""Stage 2: verify residency evidence for each candidate via SearXNG + local Ollama.

    python verify.py <region_slug>

Reads data/candidates_<region_slug>.json, writes data/verified_<region_slug>.json
with a confidence tier per candidate. No Claude session needed.

Candidates verify.py can't confidently resolve (confidence "none", or a name
ambiguous enough that search returns mixed people) are left in the output
with confidence "none" / "needs_deep_research" rather than dropped silently —
those are the ones worth escalating to a manual tinyfish/searxng-MCP pass in
a Claude session, same as the honest gap-notes in the current feed.
"""
import json
import sys

from regions import REGIONS, VERIFY_QUERY_TEMPLATE
from searxng_client import search
from ollama_client import judge_residency


def verify(region_slug: str) -> list[dict]:
    region = REGIONS[region_slug]
    with open(f"data/candidates_{region_slug}.json", encoding="utf-8") as f:
        candidates = json.load(f)

    verified = []
    for c in candidates:
        snippets = search(VERIFY_QUERY_TEMPLATE.format(name=c["name"], region=region["name"]))
        if not snippets:
            snippets = [{"title": c["name"], "content": c["discovery_snippet"], "url": c["source_url"]}]
        judgment = judge_residency(c["name"], region["name"], snippets)
        verified.append({**c, **judgment})
    return verified


if __name__ == "__main__":
    slug = sys.argv[1] if len(sys.argv) > 1 else "ohio"
    out = verify(slug)
    with open(f"data/verified_{slug}.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    high = sum(1 for v in out if v["confidence"] == "high")
    low = sum(1 for v in out if v["confidence"] == "low")
    none = sum(1 for v in out if v["confidence"] == "none")
    print(f"{slug}: {high} high, {low} low, {none} none (needs manual review) -> data/verified_{slug}.json")
