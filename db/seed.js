// ============================================================
// Database seed script
// Usage: node db/seed.js [--clean]
//   --clean : drop and recreate all tables before seeding
//
// Creates the SQLite database from schema.sql and inserts a
// small, deterministic set of demo data so that the app and the
// API have something to show on first run.
// ============================================================

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const Database = require('better-sqlite3');

const DB_PATH = process.env.DB_PATH || path.join(__dirname, 'app.db');
const SCHEMA = path.join(__dirname, 'schema.sql');
const clean = process.argv.includes('--clean');

function hash(pw) {
  return crypto.createHash('sha256').update(pw).digest('hex');
}

function isoInDays(days) {
  const d = new Date();
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

const db = new Database(DB_PATH);
db.pragma('foreign_keys = ON');

if (clean) {
  db.exec('DROP TABLE IF EXISTS tasks; DROP TABLE IF EXISTS users;');
  console.log('Dropped existing tables.');
}

// Apply schema
db.exec(fs.readFileSync(SCHEMA, 'utf8'));
console.log('Schema applied.');

// Seed users (idempotent — skip if already present)
const insertUser = db.prepare(
  'INSERT OR IGNORE INTO users (email, password_hash, display_name) VALUES (?, ?, ?)'
);
const users = [
  ['alex@example.com', hash('Password123!'), 'Alex Rivera'],
  ['sam@example.com', hash('Password123!'), 'Sam Chen'],
  ['jordan@example.com', hash('Password123!'), 'Jordan Blake'],
];
const userIds = [];
for (const u of users) {
  insertUser.run(...u);
  const row = db.prepare('SELECT id FROM users WHERE email = ?').get(u[0]);
  userIds.push(row.id);
}
console.log(`Seeded ${userIds.length} users.`);

// Seed tasks
const clearTasks = db.prepare('DELETE FROM tasks');
clearTasks.run();

const insertTask = db.prepare(
  `INSERT INTO tasks (title, description, due_date, priority, status, user_id)
   VALUES (?, ?, ?, ?, ?, ?)`
);
const demoTasks = [
  ['Prepare Q3 test plan', 'Draft the automation strategy for Q3', isoInDays(7), 'high', 'active'],
  ['Review pull request #142', 'Playwright migration PR', isoInDays(2), 'high', 'active'],
  ['Update onboarding docs', null, isoInDays(14), 'medium', 'active'],
  ['Fix flaky login test', 'Replace waitForTimeout with waitForResponse', isoInDays(-1), 'high', 'overdue'],
  ['Archive old test reports', null, isoInDays(30), 'low', 'active'],
  ['Set up nightly CI report', 'Slack webhook + metrics script', isoInDays(5), 'medium', 'active'],
  ['Write DB constraint tests', 'One test per schema constraint', isoInDays(3), 'high', 'active'],
  ['Retire Selenium suite', 'Migrated to Playwright', isoInDays(-5), 'low', 'completed'],
];
let n = 0;
demoTasks.forEach((t, i) => {
  insertTask.run(t[0], t[1], t[2], t[3], t[4], userIds[i % userIds.length]);
  n++;
});
console.log(`Seeded ${n} tasks.`);
console.log(`Database ready at ${DB_PATH}`);
db.close();
