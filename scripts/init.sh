#!/usr/bin/env bash
# ============================================================
# Course starter — initialisation script
# Usage: bash scripts/init.sh
#
# 1. Verifies prerequisites (node, python3, git, gh)
# 2. Installs API, web, and Python dependencies
# 3. Seeds the database
# 4. Initialises a git repository with a first commit
# 5. Prints how to start the app and run the tests
# ============================================================
set -e

GREEN='\033[0;32m'; RED='\033[0;31m'; YEL='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✔${NC} $1"; }
warn() { echo -e "${YEL}!${NC} $1"; }
fail() { echo -e "${RED}✘${NC} $1"; }

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo "Initialising course starter in: $ROOT"
echo

# --- 1. Prerequisites ----------------------------------------
echo "== Checking prerequisites =="
command -v node >/dev/null 2>&1 && ok "node $(node -v)" || { fail "node not found (need v20+)"; exit 1; }
command -v python3 >/dev/null 2>&1 && ok "python3 $(python3 --version 2>&1 | awk '{print $2}')" || { fail "python3 not found (need 3.11+)"; exit 1; }
command -v git >/dev/null 2>&1 && ok "git $(git --version | awk '{print $3}')" || { fail "git not found"; exit 1; }
command -v gh >/dev/null 2>&1 && ok "gh $(gh --version | head -1 | awk '{print $3}')" || warn "gh CLI not found — get_open_prs MCP tool and Copilot CLI will be unavailable"
echo

# --- 2. Dependencies -----------------------------------------
echo "== Installing dependencies =="
# Root npm workspaces install covers api/, web-app/ and tools/mcp-local/
# and hoists shared deps (better-sqlite3, @playwright/test) to the root
# node_modules so db/seed.js and tests/web can resolve them.
npm install --silent && ok "Node deps installed (workspaces: api, web-app, tools/mcp-local)" || warn "npm install failed"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv && ok "Python venv created"
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt && ok "Python deps installed" || warn "Python deps failed"
echo

# --- 3. Seed database ----------------------------------------
echo "== Seeding database =="
node db/seed.js --clean && ok "Database seeded" || warn "Seed failed"
echo

# --- 4. Environment file -------------------------------------
if [ ! -f ".env" ]; then
  cp .env.example .env && ok ".env created from .env.example"
fi
echo

# --- 5. Git init ---------------------------------------------
echo "== Initialising git =="
if [ ! -d ".git" ]; then
  git init -q -b main
  git add -A
  git -c user.name="Course Participant" -c user.email="participant@example.com" \
      commit -q -m "chore: initial course starter (Copilot for Automation Engineers)"
  ok "Git repository initialised with first commit"
else
  warn "Git repo already exists — skipping init"
fi
echo

# --- Done ----------------------------------------------------
echo -e "${GREEN}Setup complete!${NC}"
echo
echo "Next steps:"
echo "  1. Start the API:   node api/server.js &"
echo "  2. Start the web:   (cd web-app && npm run dev)"
echo "  3. Open the app:    http://localhost:3000"
echo "  4. Activate venv:   source .venv/bin/activate"
echo "  5. Run API tests:   API_BASE_URL=http://localhost:3001 pytest tests/api -v"
echo
echo "Begin with Module 1, Lab 01 in the Lab Guide."
