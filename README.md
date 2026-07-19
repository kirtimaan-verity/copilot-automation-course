# GitHub Copilot for Automation Engineers — Course Starter (Empty-Slate Edition)

This is the hands-on starter repository for the 3-day course **"GitHub Copilot
for Automation Engineers" (COPILOT-AE)**. Every lab in the Lab Guide operates
on the files in this repository.

**Empty-slate edition:** the `tests/` directories start empty (except the
`conftest.py` scaffolding). You generate every test file yourself with Copilot
during the labs — there are no pre-written answer keys to read. Each test
directory has a short `README.md` telling you what to create and in which lab.

## What's in here

| Path | What it is | Used by |
|------|-----------|---------|
| `web-app/` | React task-manager app (Vite) with `data-testid` locators | Module 1, 4, 8 (Playwright) |
| `api/` | Node/Express API + `openapi.yaml` | Module 3, 4, 9 (pytest API) |
| `db/` | `schema.sql` (constraints) + `seed.js` | Module 3, 4, 9 (DB tests) |
| `tests/` | Empty test dirs + per-folder READMEs (you fill these in) | Modules 4–9 |
| `tests/*/conftest.py` | Starting pytest fixtures (extend in labs) | Module 4 |
| `.github/copilot-instructions.md` | Repo-wide Copilot rules | Module 2, 5 |
| `.github/prompts/` | The 5-prompt reusable library + README | Module 5 Lab 19 |
| `.github/workflows/ci.yml` | Starting CI pipeline (harden in labs) | Module 2, 6, 10 |
| `tools/mcp-local/` | Working MCP server for Copilot agent mode | Module 5, 10 |
| `.vscode/mcp.json` | Wires the MCP server into VS Code | Module 5 Lab 21 |
| `docs/` | User stories, known issues (feed the labs) | Module 3, 5 |

The `tests/` directories contain only scaffolding you build on:
`conftest.py` fixtures (which you extend) and a `README.md` in each folder
listing what to generate and when. Everything else you create with Copilot.

## Prerequisites

- Node.js 22+ (24 LTS recommended — see `.nvmrc`)
- Python 3.11+
- Git
- GitHub CLI (`gh`) with an active Copilot licence
- VS Code with the GitHub Copilot + Copilot Chat extensions

## Quick start

```bash
bash scripts/init.sh
```

That installs all dependencies, seeds the database, creates `.env`, and makes
the first git commit. Then:

```bash
# Terminal 1 — API
node api/server.js

# Terminal 2 — Web app
cd web-app && npm run dev
# open http://localhost:3000

# Terminal 3 — tests (you generate these during the labs)
source .venv/bin/activate
# After Module 4 Lab 16 you'll be able to run:
#   API_BASE_URL=http://localhost:3001 pytest tests/api -v
# After Module 4 Lab 17:
#   TEST_DB_URL=sqlite:///./db/app.db pytest tests/db -v
# After Module 4 Lab 14 (from web-app/):
#   BASE_URL=http://localhost:3000 npx playwright test
```

## Running with Copilot

1. Open this folder in VS Code — the Copilot instructions apply automatically.
2. Open `.github/prompts/README.md` to see the prompt library.
3. Reload the window to activate the MCP server (`.vscode/mcp.json`), then switch
   Copilot Chat to **Agent** mode.
4. Start with **Module 1, Lab 01** in the Lab Guide.

## Layout

```
copilot-automation-course/
├── api/            # Express API + openapi.yaml
├── web-app/        # React app (Vite) + playwright.config.ts
├── db/             # schema.sql + seed.js
├── tests/          # web / mobile / api / db / e2e / performance
├── tools/mcp-local/# MCP server
├── .github/        # instructions, prompts, workflows, config
├── .vscode/        # mcp.json, settings, extensions
├── docs/           # user stories, known issues
└── scripts/init.sh # one-shot setup
```
