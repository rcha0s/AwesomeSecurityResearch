# Publishing to GitHub

This repo was built locally. Follow either path below to get it onto your GitHub.

> One-time cleanup: a partial `.git` folder may exist from the build environment.
> Delete it first so you start clean. On Windows PowerShell, from the project folder:
>
> ```powershell
> Remove-Item -Recurse -Force .git -ErrorAction SilentlyContinue
> ```

## Option A — GitHub CLI (fastest)

Requires the [GitHub CLI](https://cli.github.com/) (`gh auth login` once).

```bash
cd AwesomeSecurityResearch
git init -b main
git add -A
git commit -m "Initial commit: AwesomeSecurityResearch — security research tracker"
gh repo create AwesomeSecurityResearch --public --source=. --remote=origin --push
```

That creates the repo under your account and pushes in one step.

## Option B — Plain git

1. Create an empty repo on GitHub named **AwesomeSecurityResearch** (no README/license — this repo already has them).
2. Then:

```bash
cd AwesomeSecurityResearch
git init -b main
git add -A
git commit -m "Initial commit: AwesomeSecurityResearch — security research tracker"
git remote add origin https://github.com/<your-username>/AwesomeSecurityResearch.git
git push -u origin main
```

## After pushing

1. **Enable the render workflow.** `.github/workflows/update.yml` re-ranks the pools and regenerates the site weekly + on push. Go to **Settings → Actions → General → Workflow permissions** → **Read and write permissions**, then run it once from the **Actions** tab → *Render research site*. (It does **not** scan Twitter or run the LLM — that happens locally.)
2. **Add topics**: `security`, `ai`, `awesome`, `ai-security`, `web-security`, `mobile-security`, `agents`, `research`.
3. **Set the description**: "Auto-updating, source-cited pool of the most teachable AI and security research."

## One-time local setup (for scanning)

Twitter/article ingestion runs locally (in **WSL2**), never in CI. See [AGENTS.md](AGENTS.md).

```bash
pip install -r requirements.txt
# Agent Reach is NOT on PyPI — install from its GitHub archive:
pipx install https://github.com/Panniantong/agent-reach/archive/main.zip
agent-reach install --env=auto --channels twitter,linkedin   # --dry-run to preview
agent-reach configure --from-browser chrome   # from the browser logged into the BURNER
#   …or paste manually: agent-reach configure twitter-cookies '<cookie json>'
agent-reach doctor --json           # confirm the twitter backend is ok
```

Follow the AI/security accounts you want on the burner, and list them under
`scripts/sources.yaml → twitter.accounts`.

## Day-to-day maintenance

- **Capture one resource:** `python scripts/add.py "<url>"`, then run the **`/add-resource`** skill — it shows the teachable summary, takeaway, and action, and files it.
- **Batch scan** your X feed + RSS: run the **`/research-scan`** skill (self-pace with `/loop 12h /research-scan`).
- **Just re-render** from the pools:

  ```bash
  python scripts/rerank.py
  python scripts/generate_site.py
  python scripts/generate_skills.py
  ```

The skills extract lessons, score novelty/relevance, derive actionable leverage, merge
into `data/security.json` / `data/ai.json`, re-rank, and regenerate the site. Low-confidence
findings are flagged `needs_review` until verified.

## Further development with firstmate

This repo is onboarded to **firstmate** (see [AGENTS.md](AGENTS.md) + `data/backlog.md`).
From WSL2, launch firstmate and point it at `/mnt/c/Users/rohan/Desktop/AwesomeSecurityResearch`;
dispatch `ship`/`scout` tasks to evolve the pipeline via PRs.
