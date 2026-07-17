# Online Influencer Discovery Feed

A curated feed of tools, techniques, and projects for discovering, profiling, and
evaluating public social media influencers and creators — useful for marketing
research, brand-partner sourcing, and audience/engagement analysis.

Compiled from [GitHub's `influencer-discovery` topic](https://github.com/topics/influencer-discovery)
and [The-Osint-Toolbox/Social-Media-OSINT](https://github.com/The-Osint-Toolbox/Social-Media-OSINT).

> **Scope note:** This is a list of publicly documented tools and techniques for
> researching *public* creator/influencer accounts (marketing & audience research
> use cases). It is not intended for surveilling or de-anonymizing private
> individuals.

## Discovery & Profiling

Finding and identifying creator accounts across platforms.

- **[influencer-finder](https://github.com/topics/influencer-discovery)** — Browses influencer profiles to match brands with suitable creators (React + search).
- **[influencer-marketing-finder](https://github.com/topics/influencer-discovery)** — Discovers micro-influencers by niche category (Apify scraping, Instagram/TikTok).
- **[unifapi-mcp-server](https://github.com/topics/influencer-discovery)** — Public-data APIs/MCP skills for AI agents across Twitter, YouTube, Reddit, Instagram, LinkedIn, TikTok.
- **Username & bio-link lookups** (via Social-Media-OSINT) — Beacons, Linktree, Keybase, Gravatar aggregators for cross-platform identity resolution.

## Analytics & Vetting

Evaluating audience quality and authenticity once a creator is found.

- **[IGAudit](https://github.com/topics/influencer-discovery)** — ML-based fake-follower / fake-account detection (Random Forest, Logistic Regression, KNN via scikit-learn).
- **[tiktok-profile-scraper-python](https://github.com/topics/influencer-discovery)** — TikTok metrics without API credentials; engagement-rate calculation and creator-tier classification.
- **Engagement-rate calculators & follower auditing** (via Social-Media-OSINT) — cross-platform engagement/authenticity checks, e.g. Modash for Instagram ad/marketing analysis.

## Platform-Specific Scrapers

- **[facebook_scrape_live_gaming_page](https://github.com/topics/influencer-discovery)** — Extracts influencer data from Facebook gaming pages (Selenium, BeautifulSoup, MongoDB).
- **[instagram-profiles-scraper-ppr](https://github.com/topics/influencer-discovery)** — Instagram profile/audience data extraction.
- **[reddit-profile-scraper-python](https://github.com/topics/influencer-discovery)** — Public Reddit profile scraping for audience research (no auth required).
- **[facebook-profile-scraper-python](https://github.com/topics/influencer-discovery)** — Public Facebook profile/page extraction with verification detection.
- **[Threads-Influencer-Finder-Bot](https://github.com/topics/influencer-discovery)** — Automated Threads discovery via Appium/ADB.

## Workflow / No-Code

- **[n8n-nodes-apivault-tiktok-profile](https://github.com/topics/influencer-discovery)** / **[n8n-nodes-apivault-reddit](https://github.com/topics/influencer-discovery)** — No-code n8n nodes for creator research, Apify-backed.

## Broader OSINT Reference

For general (non-influencer-specific) social media OSINT tradecraft — covering
17+ platforms including Facebook, Instagram, X, TikTok, LinkedIn, Reddit,
Bluesky, Mastodon, Telegram, and more — see
[The-Osint-Toolbox/Social-Media-OSINT](https://github.com/The-Osint-Toolbox/Social-Media-OSINT),
which organizes tools into Discovery & Profiling, Analytics & Monitoring,
Search & Archival, and Data Extraction sections.

## Contributing

PRs welcome — add a tool with a one-line description of what it does and
which platform(s) it covers. Keep entries scoped to public creator/influencer
research use cases.

## License

MIT
