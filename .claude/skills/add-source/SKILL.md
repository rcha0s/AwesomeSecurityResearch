---
name: add-source
description: Add an approved SOURCE to the rankable registry — an X user to follow, a blog/RSS feed, a newsletter, a GitHub user, a GitHub search query, or a YouTube channel. The source is ranked and then harvested on every scan. Use when the user says "follow/add/track this account / blog / channel / newsletter / repo-author".
---

# add-source

Registers a recurring source in `data/sources.json` (the growing, rankable
registry) so it gets harvested on every `/research-scan`. This is different from
`/add-resource`, which captures ONE article/finding — this adds a *source* we
keep scanning.

## Pick the type

| User says… | type | handle |
|---|---|---|
| follow this X/Twitter user | `x_account` | `@handle` |
| track this blog / this feed | `blog` (→ rss) | site URL or feed URL (feed auto-discovered) |
| add this newsletter | `newsletter` | site/feed URL (Substack `/feed`, etc.) |
| watch this GitHub user's new work | `github_user` | `username` |
| search GitHub for X | `github_query` | `"query string"` |
| add this YouTube channel | `youtube` | channel URL / `@handle` / id |

## Steps

1. **Register it:**
   ```bash
   python scripts/add_source.py <type> "<handle>" \
     --topics <ai-security|product-security|ai-research[,...]> \
     --tier <high|medium|low> [--name "..."] [--notes "..."]
   ```
   - **topics** are the three tracked topics: `ai-security`, `product-security`,
     `ai-research`. Pick the one(s) the source mostly feeds (a source can serve
     several). If unsure, omit — findings get classified at analysis time anyway.
   - **tier** is your authority call (high = first-party/renowned researcher;
     medium = solid practitioner; low = worth watching). It anchors the rank.
   - For `x_account`, the user must also **follow the account on the burner** so
     it appears in scans (the registry lists it; the burner following surfaces it).
   - For `github_user`, follower count is fetched automatically; for others you
     may pass `--followers/--stars/--subscribers` if you know them.

2. **Confirm** the printed rank + tier + topics back to the user, and note it
   will be picked up on the next `/research-scan`. If it was already registered,
   say so (idempotent).

3. If the user is adding several at once, call `add_source.py` per source.

## Ranking (for your explanation)

`rank = 0.50·tier + 0.25·reach-signal + 0.25·hit-rate`. The hit-rate rises when
a source yields **curated** findings and falls when it yields noise, so good
sources climb over time and weak ones sink — sources compete for attention.
