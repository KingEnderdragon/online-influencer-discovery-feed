"""Thin client for a local SearXNG instance's JSON API.

Requires SearXNG running locally with `search.formats: [html, json]` enabled
in settings.yml (see README). No API key, no Claude session needed.
"""
import os
import requests

SEARXNG_URL = os.environ.get("SEARXNG_URL", "http://localhost:8080")

# Minimum count of unresponsive upstream engines (rate-limited/CAPTCHA'd) before
# we treat a zero-result response as "search is down" rather than "no matches".
RATE_LIMIT_ENGINE_THRESHOLD = 3


class RateLimited(Exception):
    """Raised when SearXNG's upstream engines are throttled rather than just
    returning no matches. Callers (discover.py / verify.py) should catch this
    and fall back to WebSearch instead of recording an empty result."""


def search(query: str, count: int = 8) -> list[dict]:
    resp = requests.get(
        f"{SEARXNG_URL}/search",
        params={"q": query, "format": "json"},
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results", [])[:count]
    unresponsive = data.get("unresponsive_engines", [])
    if not results and len(unresponsive) >= RATE_LIMIT_ENGINE_THRESHOLD:
        raise RateLimited(f"{len(unresponsive)} engines unresponsive: {unresponsive}")
    return [
        {"title": r.get("title", ""), "url": r.get("url", ""), "content": r.get("content", "")}
        for r in results
    ]
