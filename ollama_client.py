"""Thin client for a local Ollama server, used to judge residency evidence."""
import json
import os
import requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:14b")

RESIDENCY_PROMPT = """You are checking whether a piece of search-result text proves a \
person CURRENTLY lives in a specific region (not "born there", "covers it as a \
journalist", or "posts about" it).

Person: {name}
Region: {region}
Search snippets:
{snippets}

Reply with ONLY a JSON object, no other text:
{{"confidence": "high"|"low"|"none", "quote": "<shortest direct quote proving residency, or empty string>"}}

Rules:
- "high": an explicit first-person bio location tag, or a press quote stating current residency.
- "low": suggestive but indirect (e.g. business address in the region, event appearance).
- "none": no residency evidence, or evidence contradicts the region (moved away, born-there-only).
"""


def judge_residency(name: str, region: str, snippets: list[dict]) -> dict:
    snippet_text = "\n".join(f"- {s['title']}: {s['content']}" for s in snippets)
    prompt = RESIDENCY_PROMPT.format(name=name, region=region, snippets=snippet_text)
    resp = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "format": "json"},
        timeout=120,
    )
    resp.raise_for_status()
    return json.loads(resp.json()["response"])
