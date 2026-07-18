"""Stage 3: render every data/verified_<slug>.json into one static HTML page.

    python generate_static_page.py

Writes docs/index.html (same visual style as the previous hand-built
artifact). No Claude session needed.
"""
import glob
import html
import json
import os
import re

from regions import REGIONS

CSS = """
:root{--bg:#f6f4ee;--paper:#fffdf8;--ink:#1e211f;--muted:#66695f;--line:#ded9c9;
--accent:#2f5d4a;--accent-soft:#e4ece6;--ok:#2f6d3f;--ok-soft:#e3efe3;--warn:#9a5a1f;--warn-soft:#f4e9dc;}
@media (prefers-color-scheme: dark){:root{--bg:#141712;--paper:#1b1f19;--ink:#e9e6db;--muted:#9a9c8e;
--line:#333a30;--accent:#7fd6ab;--accent-soft:#223129;--ok:#7fd6ab;--ok-soft:#1d2c22;--warn:#e0a862;--warn-soft:#2e2417;}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font-family:ui-sans-serif,"Segoe UI",system-ui,sans-serif;line-height:1.5}
.wrap{max-width:1000px;margin:0 auto;padding:2.5rem 1.5rem 5rem}
h1{font-family:ui-serif,Georgia,serif;font-size:clamp(1.8rem,4vw,2.5rem);margin:0}
.dek{color:var(--muted);max-width:72ch}
.region-nav{display:flex;gap:.5rem;flex-wrap:wrap;margin-bottom:2.25rem}
.region-nav a{font-size:.78rem;text-decoration:none;color:var(--accent);background:var(--accent-soft);
border:1px solid var(--line);padding:.35em .8em;border-radius:999px}
h2.region-title{font-family:ui-serif,Georgia,serif;font-size:1.75rem;margin:3.5rem 0 .25rem;
padding-top:1.5rem;border-top:2px solid var(--line)}
h2.region-title:first-of-type{border-top:none;padding-top:0;margin-top:0}
h3{font-family:ui-serif,Georgia,serif;font-size:1.3rem;margin:0 0 .5rem}
.status-badge{font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.04em;
padding:.25em .65em;border-radius:999px}
.status-badge.high{background:var(--ok-soft);color:var(--ok)}
.status-badge.low{background:var(--warn-soft);color:var(--warn)}
.table-scroll{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--paper);margin-bottom:2rem}
table{width:100%;border-collapse:collapse;min-width:700px}
thead th{text-align:left;font-size:.7rem;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);
padding:.65rem .8rem;border-bottom:1px solid var(--line)}
tbody td{padding:.55rem .8rem;border-bottom:1px solid var(--line);font-size:.87rem;vertical-align:top}
.handle{font-family:ui-monospace,Consolas,monospace;color:var(--muted);font-size:.82rem}
.gap-note{font-size:.78rem;color:var(--muted);margin:0 0 2rem}
.spotlight{border:1px solid var(--accent);border-radius:10px;background:var(--accent-soft);
padding:1.1rem 1.2rem 1.3rem;margin-bottom:2.5rem}
.spotlight h3{margin-top:0}
.spotlight .table-scroll{background:var(--paper);margin-bottom:0}
.category-tag{font-size:.68rem;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}
"""


def display_name(e: dict) -> str:
    """Prefer the actual handle/username over the raw search-result title,
    since titles are often a video caption or article headline, not the
    creator's name (e.g. "RANTS FROM THE SHOWER" instead of @nickfromohio)."""
    if e.get("handle"):
        return f"@{e['handle']}"
    return e["name"]


def render_table(entries: list[dict], show_category: bool = False) -> str:
    rows = []
    for e in entries:
        cat_cell = f"<td class='category-tag'>{html.escape(e.get('category') or '')}</td>" if show_category else ""
        rows.append(
            f"<tr><td>{html.escape(display_name(e))}</td>"
            f"<td class='handle'>{html.escape(e['name']) if e.get('handle') else ''}</td>"
            f"<td><span class='status-badge {e['confidence']}'>{e['confidence']}</span></td>"
            f"{cat_cell}"
            f"<td>{html.escape(e.get('quote') or '')}</td>"
            f"<td><a href='{html.escape(e['source_url'])}' target='_blank' rel='noopener'>source</a></td></tr>"
        )
    return "\n".join(rows)


def render_region(slug: str, region: dict) -> str:
    categorized_path = f"data/categorized_{slug}.json"
    path = categorized_path if os.path.exists(categorized_path) else f"data/verified_{slug}.json"
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as f:
        entries = json.load(f)
    has_categories = path == categorized_path

    confirmed = [e for e in entries if e["confidence"] in ("high", "low")]
    needs_review = [e for e in entries if e["confidence"] == "none"]

    # Spotlight: people who blog about a specific job/profession, called out on
    # top of (not instead of) the full listing below.
    spotlight = ""
    if has_categories:
        occupational = [e for e in confirmed if e.get("category") == "occupational"]
        if occupational:
            spotlight = f"""
            <div class="spotlight">
              <h3>Job &amp; Career Creators</h3>
              <div class="table-scroll">
                <table>
                  <thead><tr><th>Name</th><th>Source title</th><th>Confidence</th><th>Residency evidence</th><th>Source</th></tr></thead>
                  <tbody>{render_table(occupational)}</tbody>
                </table>
              </div>
            </div>
            """

    by_platform: dict[str, list] = {}
    for e in confirmed:
        by_platform.setdefault(e["platform"], []).append(e)

    header_cols = "<th>Name</th><th>Source title</th><th>Confidence</th>"
    if has_categories:
        header_cols += "<th>Category</th>"
    header_cols += "<th>Residency evidence</th><th>Source</th>"

    sections = []
    for platform, plat_entries in by_platform.items():
        sections.append(f"""
        <h3>{platform.title()}</h3>
        <div class="table-scroll">
          <table>
            <thead><tr>{header_cols}</tr></thead>
            <tbody>{render_table(plat_entries, show_category=has_categories)}</tbody>
          </table>
        </div>
        """)

    gap_note = ""
    if needs_review:
        names = ", ".join(html.escape(e["name"]) for e in needs_review[:15])
        gap_note = f"<p class='gap-note'>Flagged for manual review (no automated residency evidence found): {names}</p>"

    return f"""
    <h2 class="region-title" id="region-{slug}">{region['name']}</h2>
    {spotlight}
    {''.join(sections)}
    {gap_note}
    """


def main():
    nav = " ".join(f'<a href="#region-{slug}">{r["name"]}</a>' for slug, r in REGIONS.items())
    body = "".join(render_region(slug, r) for slug, r in REGIONS.items())

    page = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Online Influencer Discovery Feed</title>
<style>{CSS}</style></head><body>
<div class="wrap">
  <header><h1>Online Influencer Discovery Feed</h1>
  <p class="dek">Generated by discover.py + verify.py (SearXNG search, local Ollama residency
  judging) — no live Claude research per update. Entries flagged "needs manual review" are the
  ones worth a one-off tinyfish/searxng deep-dive in a Claude session.</p></header>
  <div class="region-nav">{nav}</div>
  {body}
</div></body></html>"""

    os.makedirs("docs", exist_ok=True)
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(page)
    print("wrote docs/index.html")


if __name__ == "__main__":
    main()
