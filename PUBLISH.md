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

1. **Enable the weekly auto-update.** The workflow in `.github/workflows/update.yml` runs every Monday and on demand. In the repo, go to **Settings → Actions → General → Workflow permissions** and select **Read and write permissions** so it can commit refreshed data. Then trigger it once from the **Actions** tab → *Update security research* → **Run workflow**.
2. **Add topics** for discoverability: `security`, `awesome`, `ai-security`, `web-security`, `mobile-security`, `threat-intelligence`.
3. **Set the description**: "Continuously updated, source-cited tracker of new AI, web, and mobile security research."

## Day-to-day maintenance

```bash
pip install -r requirements.txt
python scripts/aggregate.py        # pull newly published research into data/research.json
python scripts/generate_readme.py  # rebuild README.md
```

Auto-discovered items are flagged `pending review`. Promote one by writing its threat / conditions / mitigations, setting a severity, and flipping `needs_review` to `false` in `data/research.json`, then regenerate.
