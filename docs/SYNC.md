# GitHub + Gitee Dual-Platform Sync

This project is maintained on both **GitHub** (international) and **Gitee** (China).

| Platform | URL Pattern | Audience |
|----------|-------------|----------|
| **GitHub** | `github.com/your-name/free-ai-router` | International developers, stars, contributions |
| **Gitee** | `gitee.com/your-name/free-ai-router` | Chinese developers, fast access in China, Gitee Go |

---

## Why Both?

- **GitHub** has the largest open-source community, best for international visibility
- **Gitee** is faster in mainland China, has built-in code review (Gitee Go), and is the de-facto standard for Chinese open-source projects
- Syncing to both means **double the visibility** with minimal extra effort

---

## Initial Setup

### 1. Create Accounts

- **GitHub:** https://github.com/signup
- **Gitee:** https://gitee.com/signup (real-name verification recommended for full features)

### 2. Create Empty Repos on Both

- **GitHub:** https://github.com/new
  - Name: `free-ai-router`
  - Public
  - **Do NOT** initialize with README, .gitignore, or license (we already have these)

- **Gitee:** https://gitee.com/projects/new
  - Name: `free-ai-router`
  - Public
  - **Do NOT** initialize (avoid "use Gitee recommended files" option)

### 3. Add Remotes

In your local repo:

```bash
# GitHub (primary, international)
git remote add github https://github.com/fast118/free-ai-router.git

# Gitee (primary, China)
git remote add gitee https://gitee.com/wudijia2026/free-ai-router.git

# Verify
git remote -v
```

---

## Daily Workflow

### Push to Both

```bash
# Push to GitHub
git push github main

# Push to Gitee
git push gitee main
```

Or, set up a one-command push:

```bash
# Add to your .bashrc / .zshrc / PowerShell profile
alias pushall="git push github main && git push gitee main"
```

### Pull from Both

```bash
git pull github main
git pull gitee main
```

Or, configure one as the primary pull source:

```bash
git branch --set-upstream-to=github/main main
```

---

## Auto-Sync (Advanced)

For automatic sync, use **GitHub Actions** to mirror GitHub → Gitee:

### Step 1: Create Gitee Password Token

1. Gitee → Settings → Private Tokens → Generate new token
2. Scope: `projects` (read/write)
3. Copy the token

### Step 2: Add to GitHub Secrets

1. GitHub → Your repo → Settings → Secrets and variables → Actions
2. New repository secret:
   - Name: `GITEE_TOKEN`
   - Value: paste the Gitee token

### Step 3: Create Workflow File

`.github/workflows/sync-to-gitee.yml`:

```yaml
name: Sync to Gitee

on:
  push:
    branches: [main]

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Sync to Gitee
        uses: wearerequired/git-mirror-action@v1
        with:
          source-repo: "github.com/${{ github.repository }}"
          destination-repo: "gitee.com/YOUR_GITEE_USERNAME/free-ai-router.git"
          ssh-private-key: ${{ secrets.GITEE_TOKEN }}
```

Now every push to GitHub will auto-sync to Gitee. No manual work needed.

---

## Issue & PR Sync

- **Issues & PRs** are NOT auto-synced
- For international users: direct them to GitHub
- For Chinese users: direct them to Gitee
- Mention both URLs in README

---

## Why Not Use Gitee as Primary?

- Gitee has occasional outages
- Some open-source tooling (Dependabot, etc.) only works on GitHub
- Most international contributors are on GitHub
- **Recommended: GitHub as primary (canonical), Gitee as mirror**

---

## Repository Settings

### GitHub Recommended Settings

- Default branch: `main`
- Allow squash merging only (clean history)
- Enable auto-delete head branches
- Enable vulnerability alerts
- Enable discussions

### Gitee Recommended Settings

- Default branch: `main`
- Enable Pull Request reviews
- Enable Gitee Go (CI/CD)
- Issue templates: import from GitHub

---

## Stats & Badges

Add these to your README to show both:

```markdown
[![GitHub stars](https://img.shields.io/github/stars/USER/REPO)](https://github.com/USER/REPO)
[![Gitee stars](https://gitee.com/USER/REPO/badge/star.svg)](https://gitee.com/USER/REPO)
[![GitHub forks](https://img.shields.io/github/forks/USER/REPO)](https://github.com/USER/REPO)
[![Gitee forks](https://gitee.com/USER/REPO/badge/fork.svg)](https://gitee.com/USER/REPO)
```
