# PR Review Agent — Claude

An automated Pull Request review agent powered by **Claude (Anthropic)** that runs in a **GitHub Actions** pipeline. When a PR is opened or updated, the agent fetches the changed files, sends them to Claude for analysis, and posts **inline comments** directly on the PR with actionable feedback.

---

## How It Works

```
GitHub PR opened/updated
        │
        ▼
GitHub Actions triggers agent.py
        │
        ├─► Fetch PR head commit SHA
        ├─► Fetch full unified diff of the PR
        ├─► Parse diff → split by file
        │       └─ Filter by allowed extensions & excluded files (config.json)
        │
        ├─► For each changed file:
        │       ├─ Fetch full file content (for conflict detection)
        │       ├─ Load domain knowledge rules (skills.md / DOMAIN_RULES.md)
        │       └─ Send diff + full file + rules → Claude API
        │
        └─► Post inline review comments on the PR
```

### Review Categories

Claude analyzes each changed file and flags issues across four categories:

| Category | Description |
|---|---|
| `GUIDELINE` | Violations of project-specific rules defined in `skills.md` |
| `CORRECTNESS` | Logic errors, wrong types, off-by-one errors, bad assumptions |
| `FAILURE_RISK` | Runtime failures — null values, missing error handling, edge cases |
| `CONFLICT` | New changes that break or conflict with existing code in the same file |

Each inline comment follows the format:
```
[SEVERITY] [CATEGORY] <message>
```
e.g. `[ERROR] [CONFLICT] Function renamed to func_calculate but still called as calculate on line 42`

---

## Skills (Domain Knowledge)

The agent loads project-specific review rules from `skills.md` (or `DOMAIN_RULES.md` if present). Claude uses these rules as a guide during review, in addition to general best practices.

**Example `skills.md`:**
```markdown
# Guidelines for Python Files
- All python functions should start with func_ as prefix. eg: func_calculate

# Guidelines for SQL Files
- All SQL keywords must be UPPERCASE.
- Every table must have id, created_at, and updated_at columns.
- Avoid SELECT *; always list columns explicitly.
```

To customize rules for your project, simply edit `skills.md` at the root of the repository.

---

## Configuration

All tunable settings live in `config.json` — no code changes needed:

```json
{
    "model_id": "claude-sonnet-4-6",
    "allowed_extensions": [".py", ".sql", ".java"],
    "excluded_files": ["agent.py"],
    "github_api_base": "https://api.github.com",
    "max_tokens": 8096
}
```

| Key | Description |
|---|---|
| `model_id` | Claude model to use for reviews |
| `allowed_extensions` | Only files with these extensions will be reviewed |
| `excluded_files` | Specific filenames to skip (e.g. the agent itself) |
| `github_api_base` | GitHub API base URL |
| `max_tokens` | Max tokens for Claude's response (~100–160 recommendations) |

---

## Setup Guide

### Prerequisites
- A GitHub repository you want to add PR review to
- An [Anthropic API key](https://console.anthropic.com/)

### Step 1 — Add the agent files to your repository

Copy these files into the root of your repository:
```
agent.py
config.json
skills.md
```

### Step 2 — Add the Anthropic API key as a GitHub Secret

1. Go to your repository → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `ANTHROPIC_API_KEY`
4. Value: your Anthropic API key

> `GITHUB_TOKEN` and `GITHUB_REPOSITORY` are automatically provided by GitHub Actions — no setup needed.

### Step 3 — Create the GitHub Actions workflow

Create the file `.github/workflows/pr-review.yml` in your repository:

```yaml
name: PR Review Agent

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
      contents: read

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install anthropic requests python-dotenv

      - name: Run PR Review Agent
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
        run: python agent.py
```

### Step 4 — Customize your rules

Edit `skills.md` to add project-specific guidelines for Claude to enforce during reviews. You can add sections for any language (Python, SQL, Java, etc.).

### Step 5 — Open a Pull Request

Create or update a PR in your repository. The GitHub Actions workflow will trigger automatically, and inline review comments will appear on the changed files within the PR.

---

## Limits

| Limit | Value |
|---|---|
| Input context window | 200,000 tokens (~600,000 characters) |
| Output (`max_tokens`) | 8,096 tokens (configurable in `config.json`) |
