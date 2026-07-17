"""Thin client for a local SearXNG instance's JSON API.

Requires SearXNG running locally with `search.formats: [html, json]` enabled
in settings.yml (see README). No API key, no Claude session needed.
"""
import os
import requests

SEARXNG_URL = os.environ.get("SEARXNG_URL", "http://localhost:8080")


def search(query: str, count: int = 8) -> list[dict]:
    resp = requests.get(
        f"{SEARXNG_URL}/search",
        params={"q": query, "format": "json"},
        timeout=20,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])[:count]
    return [
        {"title": r.get("title", ""), "url": r.get("url", ""), "content": r.get("content", "")}
        for r in results
    ]
