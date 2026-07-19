// ============================================================
// Task routes — /tasks endpoints
// Referenced by: Module 3 (Planner), Module 4 Lab 16 (API tests),
//                Module 7 (Verifier), Module 9 (security tests)
//
// Validation rules enforced here (and mirrored in db/schema.sql):
//   - title: required, 1..200 chars
//   - description: optional, <= 2000 chars
//   - priority: one of low|medium|high (default medium)
//   - due_date: optional; if present must be today or future
//   - status: one of active|completed|overdue|archived
// ============================================================

const express = require('express');
const router = express.Router();
const db = require('../models/db');

const VALID_PRIORITIES = ['low', 'medium', 'high'];
const VALID_STATUSES = ['active', 'completed', 'overdue', 'archived'];

// --- Validation helper ---------------------------------------
function validateTask(body, { partial = false } = {}) {
  const errors = [];

  if (!partial || body.title !== undefined) {
    if (body.title === undefined || body.title === null || body.title === '') {
      errors.push('Title is required');
    } else if (typeof body.title !== 'string') {
      errors.push('Title must be a string');
    } else if (body.title.length > 200) {
      errors.push('Title must not exceed 200 characters');
    }
  }

  if (body.description !== undefined && body.description !== null) {
    if (body.description.length > 2000) {
      errors.push('Description must not exceed 2000 characters');
    }
  }

  if (body.priority !== undefined && body.priority !== null) {
    if (!VALID_PRIORITIES.includes(body.priority)) {
      errors.push(`Priority must be one of: ${VALID_PRIORITIES.join(', ')}`);
    }
  }

  if (body.status !== undefined && body.status !== null) {
    if (!VALID_STATUSES.includes(body.status)) {
      errors.push(`Status must be one of: ${VALID_STATUSES.join(', ')}`);
    }
  }

  if (body.due_date !== undefined && body.due_date !== null && body.due_date !== '') {
    const due = new Date(body.due_date);
    if (isNaN(due.getTime())) {
      errors.push('Due date must be a valid date (YYYY-MM-DD)');
    } else {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      if (due < today) {
        errors.push('Due date must be today or in the future');
      }
    }
  }

  return errors;
}

function rowToTask(row) {
  return {
    id: row.id,
    title: row.title,
    description: row.description,
    due_date: row.due_date,
    priority: row.priority,
    status: row.status,
    user_id: row.user_id,
    created_at: row.created_at,
    updated_at: row.updated_at,
  };
}

// --- GET /tasks ----------------------------------------------
// Query params: status, priority, search, user_id
router.get('/', (req, res) => {
  try {
    const clauses = [];
    const params = [];
    if (req.query.status) { clauses.push('status = ?'); params.push(req.query.status); }
    if (req.query.priority) { clauses.push('priority = ?'); params.push(req.query.priority); }
    if (req.query.user_id) { clauses.push('user_id = ?'); params.push(req.query.user_id); }
    if (req.query.search) {
      clauses.push('(title LIKE ? OR description LIKE ?)');
      const term = `%${req.query.search}%`;
      params.push(term, term);
    }
    const where = clauses.length ? `WHERE ${clauses.join(' AND ')}` : '';
    const rows = db.prepare(
      `SELECT * FROM tasks ${where} ORDER BY created_at DESC`
    ).all(...params);
    res.json(rows.map(rowToTask));
  } catch (err) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// --- GET /tasks/:id ------------------------------------------
router.get('/:id', (req, res) => {
  try {
    const row = db.prepare('SELECT * FROM tasks WHERE id = ?').get(req.params.id);
    if (!row) return res.status(404).json({ error: 'Task not found' });
    res.json(rowToTask(row));
  } catch (err) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// --- POST /tasks ---------------------------------------------
router.post('/', (req, res) => {
  try {
    const errors = validateTask(req.body);
    if (errors.length) return res.status(400).json({ error: errors.join('; '), errors });

    const info = db.prepare(
      `INSERT INTO tasks (title, description, due_date, priority, status, user_id)
       VALUES (@title, @description, @due_date, @priority, @status, @user_id)`
    ).run({
      title: req.body.title,
      description: req.body.description ?? null,
      due_date: req.body.due_date ?? null,
      priority: req.body.priority ?? 'medium',
      status: req.body.status ?? 'active',
      user_id: req.body.user_id ?? null,
    });
    const row = db.prepare('SELECT * FROM tasks WHERE id = ?').get(info.lastInsertRowid);
    res.status(201).json(rowToTask(row));
  } catch (err) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// --- PUT /tasks/:id ------------------------------------------
router.put('/:id', (req, res) => {
  try {
    const existing = db.prepare('SELECT * FROM tasks WHERE id = ?').get(req.params.id);
    if (!existing) return res.status(404).json({ error: 'Task not found' });

    const errors = validateTask(req.body, { partial: true });
    if (errors.length) return res.status(400).json({ error: errors.join('; '), errors });

    const merged = {
      title: req.body.title ?? existing.title,
      description: req.body.description ?? existing.description,
      due_date: req.body.due_date ?? existing.due_date,
      priority: req.body.priority ?? existing.priority,
      status: req.body.status ?? existing.status,
      id: req.params.id,
    };
    db.prepare(
      `UPDATE tasks SET title=@title, description=@description, due_date=@due_date,
       priority=@priority, status=@status WHERE id=@id`
    ).run(merged);
    const row = db.prepare('SELECT * FROM tasks WHERE id = ?').get(req.params.id);
    res.json(rowToTask(row));
  } catch (err) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// --- DELETE /tasks/:id ---------------------------------------
router.delete('/:id', (req, res) => {
  try {
    const info = db.prepare('DELETE FROM tasks WHERE id = ?').run(req.params.id);
    if (info.changes === 0) return res.status(404).json({ error: 'Task not found' });
    res.status(204).send();
  } catch (err) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
