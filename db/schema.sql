-- ============================================================
-- Task Manager — Database Schema
-- Used by: Module 3 (Planner), Module 4 Lab 17 (DB tests),
--          Module 9 Lab 35 (cross-layer E2E)
--
-- This schema intentionally contains a range of constraint types
-- (NOT NULL, UNIQUE, CHECK, FOREIGN KEY, CASCADE, DEFAULT) so that
-- Lab 17 can generate one test per constraint.
-- ============================================================

-- Users table --------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    display_name  TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Tasks table --------------------------------------------------
CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL
                CHECK (length(title) >= 1 AND length(title) <= 200),
    description TEXT
                CHECK (description IS NULL OR length(description) <= 2000),
    due_date    TEXT,          -- ISO date string YYYY-MM-DD (nullable)
    priority    TEXT NOT NULL DEFAULT 'medium'
                CHECK (priority IN ('low', 'medium', 'high')),
    status      TEXT NOT NULL DEFAULT 'active'
                CHECK (status IN ('active', 'completed', 'overdue', 'archived')),
    user_id     INTEGER
                REFERENCES users(id) ON DELETE CASCADE,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Indexes ------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_tasks_user_id  ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status   ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);

-- Trigger: keep updated_at fresh on UPDATE ---------------------
CREATE TRIGGER IF NOT EXISTS trg_tasks_updated_at
AFTER UPDATE ON tasks
FOR EACH ROW
BEGIN
    UPDATE tasks SET updated_at = datetime('now') WHERE id = OLD.id;
END;
