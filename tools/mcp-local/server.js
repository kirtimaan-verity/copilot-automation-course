#!/usr/bin/env node
// ============================================================
// Local MCP server — course project context for Copilot agent mode
// Referenced in Module 5 Lab 21 (built) and Module 10 Lab 40 (extended).
//
// This is a WORKING reference implementation. Students generate their
// own version during the labs; this one lets the .vscode/mcp.json
// config work out of the box.
//
// Exposes four tools:
//   list_test_files      — inventory of test files with line counts
//   get_coverage_summary — reads reports/coverage.json if present
//   list_open_issues     — reads docs/known-issues.md
//   get_open_prs         — runs `gh pr list` (requires gh auth)
//
// Transport: stdio. Logs go to stderr (stdout is the MCP protocol).
// ============================================================

const { McpServer } = require('@modelcontextprotocol/sdk/server/mcp.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const REPO_ROOT = path.join(__dirname, '..', '..');

function log(msg) {
  process.stderr.write(`[mcp] ${msg}\n`);
}

function countLines(file) {
  try {
    return fs.readFileSync(file, 'utf8').split('\n').length;
  } catch {
    return 0;
  }
}

function walkTests(dir, acc) {
  let entries = [];
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return acc;
  }
  for (const e of entries) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) {
      if (e.name === 'node_modules' || e.name === '__pycache__') continue;
      walkTests(full, acc);
    } else if (e.name.endsWith('.spec.ts') || (e.name.startsWith('test_') && e.name.endsWith('.py'))) {
      acc.push({ path: path.relative(REPO_ROOT, full), lines: countLines(full) });
    }
  }
  return acc;
}

function runGh(args) {
  return new Promise((resolve, reject) => {
    const proc = spawn('gh', args, { stdio: ['pipe', 'pipe', 'pipe'] });
    let out = '';
    let err = '';
    proc.stdout.on('data', (d) => (out += d));
    proc.stderr.on('data', (d) => (err += d));
    proc.on('close', (code) => (code === 0 ? resolve(out) : reject(new Error(err || 'gh failed'))));
    proc.on('error', reject);
  });
}

const server = new McpServer({ name: 'course-data', version: '1.1.0' });

server.tool('list_test_files', 'Lists all test files with their line counts', {}, async () => {
  try {
    const files = walkTests(path.join(REPO_ROOT, 'tests'), []);
    const text = files.length
      ? files.map((f) => `${f.path} (${f.lines} lines)`).join('\n')
      : 'No test files found yet.';
    return { content: [{ type: 'text', text }] };
  } catch (e) {
    return { content: [{ type: 'text', text: `Error: ${e.message}` }] };
  }
});

server.tool('get_coverage_summary', 'Reads the latest coverage report if present', {}, async () => {
  try {
    // c8 json-summary output (API coverage — Module 7 Lab 28)
    const c8Path = path.join(REPO_ROOT, 'reports', 'coverage-summary.json');
    if (fs.existsSync(c8Path)) {
      const data = JSON.parse(fs.readFileSync(c8Path, 'utf8'));
      const pct = data?.total?.lines?.pct ?? 'unknown';
      return { content: [{ type: 'text', text: `API line coverage: ${pct}%` }] };
    }
    // pytest-cov json output (fallback)
    const pyPath = path.join(REPO_ROOT, 'reports', 'coverage.json');
    if (fs.existsSync(pyPath)) {
      const data = JSON.parse(fs.readFileSync(pyPath, 'utf8'));
      const pct = data?.totals?.percent_covered?.toFixed?.(1) ?? 'unknown';
      return { content: [{ type: 'text', text: `Total coverage: ${pct}%` }] };
    }
    return { content: [{ type: 'text', text: 'No coverage report found. Run the coverage flow from Lab 28 first.' }] };
  } catch (e) {
    return { content: [{ type: 'text', text: `Error: ${e.message}` }] };
  }
});

server.tool('list_open_issues', 'Lists known issues from docs/known-issues.md', {}, async () => {
  try {
    const p = path.join(REPO_ROOT, 'docs', 'known-issues.md');
    if (!fs.existsSync(p)) {
      return { content: [{ type: 'text', text: 'No known-issues file found.' }] };
    }
    return { content: [{ type: 'text', text: fs.readFileSync(p, 'utf8') }] };
  } catch (e) {
    return { content: [{ type: 'text', text: `Error: ${e.message}` }] };
  }
});

server.tool('get_open_prs', 'Lists open GitHub PRs for this repository', {}, async () => {
  try {
    const raw = await runGh(['pr', 'list', '--json', 'number,title,state,url', '--state', 'open']);
    const prs = JSON.parse(raw);
    const text = prs.length === 0
      ? 'No open PRs.'
      : prs.map((p) => `#${p.number}: ${p.title}`).join('\n');
    return { content: [{ type: 'text', text }] };
  } catch (e) {
    return { content: [{ type: 'text', text: `Error: ${e.message} (is gh authenticated?)` }] };
  }
});

async function main() {
  log('course-data MCP server starting (v1.1.0)');
  await server.connect(new StdioServerTransport());
}

main().catch((e) => {
  log(`fatal: ${e.message}`);
  process.exit(1);
});
