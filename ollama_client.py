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


CATEGORY_PROMPT = """You are classifying an online creator/influencer by what their content is \
mainly about, based on their name and a search snippet describing them.

Name: {name}
Platform: {platform}
Snippet: {snippet}

Reply with ONLY a JSON object, no other text:
{{"category": "occupational"|"food"|"lifestyle"|"other", "reason": "<one short phrase>"}}

Category definitions:
- "occupational": the person has a specific job/profession (nurse, electrician, teacher, \
lawyer, farmer, cop, realtor, tradesperson, small-business owner, etc.) and their content is \
mainly about that job — day-in-the-life, industry tips, workplace stories. This is the ONLY \
category we want to keep.
- "food": cooking, recipes, restaurant reviews, food tours.
- "lifestyle": vlogging, fashion, beauty, fitness/wellness, travel, general "day in my life" \
content NOT tied to a specific profession, family/mommy content, comedy/entertainment.
- "other": can't tell, or doesn't fit the above (news commentary, politics, sports fandom, \
directory/aggregator listing pages, department/institution pages, etc).

When in doubt between "occupational" and something else, only pick "occupational" if a \
specific job or profession is clearly named or evident.

Journalists, reporters, and newscasters are NEVER "occupational" even though journalism is a \
job — classify them as "other". Directory or "Top N influencers" list pages, and official \
department/institution pages (not an individual person), are also "other", not "occupational".
"""


def classify_category(name: str, platform: str, snippet: str) -> dict:
    prompt = CATEGORY_PROMPT.format(name=name, platform=platform, snippet=snippet)
    resp = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "format": "json"},
        timeout=120,
    )
    resp.raise_for_status()
    return json.loads(resp.json()["response"])
