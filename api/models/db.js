// ============================================================
// Database access layer
// Opens the SQLite database and exposes a shared connection with
// foreign key enforcement enabled.
// ============================================================

const path = require('path');
const Database = require('better-sqlite3');

const DB_PATH = process.env.DB_PATH || path.join(__dirname, '..', '..', 'db', 'app.db');

const db = new Database(DB_PATH);
db.pragma('foreign_keys = ON');
db.pragma('journal_mode = WAL');

module.exports = db;
