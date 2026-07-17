"""Region + platform config, in the spirit of political-future-news/subjects.py.

Add a new region by adding an entry to REGIONS. `search_terms` should be
locations/aliases that plausibly appear in a bio or press quote as direct
residency evidence (not just "covers X" or "posts about X").
"""

PLATFORMS = ["tiktok", "youtube", "instagram", "twitter", "facebook"]

REGIONS = {
    "ohio": {
        "name": "Ohio",
        "search_terms": ["Ohio", "Columbus, OH", "Cleveland, OH", "Cincinnati, OH", "Akron, OH", "Dayton, OH", "Toledo, OH"],
    },
    "detroit": {
        "name": "Detroit",
        "search_terms": ["Detroit, MI", "Detroit, Michigan", "metro Detroit"],
    },
    "fortwayne": {
        "name": "Fort Wayne",
        "search_terms": ["Fort Wayne, IN", "Fort Wayne, Indiana"],
    },
    "annarbor": {
        "name": "Ann Arbor",
        "search_terms": ["Ann Arbor, MI", "Ann Arbor, Michigan"],
    },
    "pennsylvania": {
        "name": "Pennsylvania",
        "search_terms": ["Pennsylvania", "Philadelphia, PA", "Pittsburgh, PA"],
    },
}

DISCOVERY_QUERY_TEMPLATES = {
    "tiktok": [
        'site:tiktok.com "{region}" bio creator',
        'top {region} tiktok influencers 2026',
    ],
    "youtube": [
        'site:youtube.com "{region}" creator channel about',
        'top {region} youtubers based in {region}',
    ],
    "instagram": [
        'site:instagram.com "{region}" influencer bio',
        'top {region} instagram influencers local',
    ],
    "twitter": [
        '{region} independent blogger twitter/x local creator',
    ],
    "facebook": [
        'site:facebook.com "{region}" blogger page',
        '{region} local blogger facebook page',
    ],
}

VERIFY_QUERY_TEMPLATE = '"{name}" lives OR resides OR based "{region}"'
