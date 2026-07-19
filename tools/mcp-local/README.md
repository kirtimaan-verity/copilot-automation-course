# course-data MCP Server

Exposes project context to Copilot agent mode (Module 5 Lab 21, Module 10 Lab 40).

## Setup
```
cd tools/mcp-local
npm install
```

## Tools
| Tool | Returns |
|------|---------|
| `list_test_files` | Test file inventory with line counts |
| `get_coverage_summary` | Total coverage % from reports/coverage.json |
| `list_open_issues` | Contents of docs/known-issues.md |
| `get_open_prs` | Open GitHub PRs (requires `gh auth login`) |

## Use in VS Code
`.vscode/mcp.json` starts this server automatically. Switch Copilot Chat to
**Agent** mode, then ask e.g. "Using course-data tools, which test files are
incomplete?"
