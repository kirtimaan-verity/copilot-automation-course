Updated todo list

Most valuable integrity tests from this schema are the ones that prove behavior, not just schema text. Use schema.sql as the source of truth and validate both acceptance and rejection paths.

**High-Value Rules To Validate**

1. Users required fields and uniqueness
- users.email is required and unique.
- users.password_hash is required.
- users.display_name is required.
- users.created_at gets a default timestamp.

2. Tasks required fields and bounds
- tasks.title is required and length 1..200.
- tasks.description is optional but max 2000 when present.
- tasks.priority must be one of low, medium, high.
- tasks.status must be one of active, completed, overdue, archived.
- tasks.priority defaults to medium.
- tasks.status defaults to active.
- tasks.created_at and tasks.updated_at default to current timestamp.

3. Foreign key integrity and cascade
- tasks.user_id must reference users.id when not null.
- deleting a user deletes their tasks via ON DELETE CASCADE.

4. Update trigger correctness
- updating a task should advance tasks.updated_at via trg_tasks_updated_at.

5. Index presence and practical usage
- idx_tasks_user_id, idx_tasks_status, idx_tasks_priority should exist.
- common filters should use these indexes in query plans.

6. Important gap to explicitly test and document
- due_date has a comment saying ISO date, but no DB CHECK enforces format.
- DB currently accepts any text for due_date unless API blocks it.
- Write a test that exposes this so the team decides whether to enforce at DB level.

**Most Valuable SQL Assertions**

1. Required and unique constraints
```sql
INSERT INTO users (email, password_hash, display_name)
VALUES ('u1@example.com', 'h', 'User 1');

-- Should fail (UNIQUE)
INSERT INTO users (email, password_hash, display_name)
VALUES ('u1@example.com', 'h2', 'User 2');
```

2. Title constraint boundaries
```sql
-- Should fail (NOT NULL/CHECK)
INSERT INTO tasks (title) VALUES (NULL);

-- Should fail (CHECK length >= 1)
INSERT INTO tasks (title) VALUES ('');

-- Should pass (exactly 200 chars)
INSERT INTO tasks (title) VALUES (substr('x',1,0) || printf('%0200d',0));
```
Better practical 200-char test:
```sql
INSERT INTO tasks (title) VALUES (replace(hex(zeroblob(100)), '00', 'a'));
```

3. Description max length
```sql
-- Should pass at 2000 chars
INSERT INTO tasks (title, description)
VALUES ('ok', replace(hex(zeroblob(1000)), '00', 'a'));

-- Should fail at 2001 chars
INSERT INTO tasks (title, description)
VALUES ('too long', replace(hex(zeroblob(1001)), '00', 'a'));
```

4. Enum checks and defaults
```sql
-- Should pass with defaults
INSERT INTO tasks (title) VALUES ('default check');
SELECT priority, status FROM tasks WHERE id = last_insert_rowid();
-- Assert: medium, active

-- Should fail invalid enum
INSERT INTO tasks (title, priority) VALUES ('bad priority', 'urgent');
INSERT INTO tasks (title, status) VALUES ('bad status', 'paused');
```

5. Foreign key and cascade
```sql
PRAGMA foreign_keys = ON;

INSERT INTO users (email, password_hash, display_name)
VALUES ('owner@example.com', 'h', 'Owner');

INSERT INTO tasks (title, user_id)
VALUES ('owned task', last_insert_rowid());

DELETE FROM users WHERE email = 'owner@example.com';

SELECT COUNT(*) FROM tasks WHERE title = 'owned task';
-- Assert: 0
```

6. Trigger updated_at
```sql
INSERT INTO tasks (title) VALUES ('trigger test');
SELECT id, updated_at FROM tasks WHERE id = last_insert_rowid();

UPDATE tasks SET title = 'trigger test updated' WHERE id = last_insert_rowid();
SELECT updated_at FROM tasks WHERE id = last_insert_rowid();
-- Assert updated_at changed to a later value
```

7. Schema drift assertions (very valuable in CI)
```sql
SELECT name FROM sqlite_master
WHERE type='index' AND tbl_name='tasks'
ORDER BY name;
-- Assert includes idx_tasks_user_id, idx_tasks_status, idx_tasks_priority

SELECT name FROM sqlite_master
WHERE type='trigger' AND name='trg_tasks_updated_at';
-- Assert one row exists
```

8. Index usage sanity checks
```sql
EXPLAIN QUERY PLAN SELECT * FROM tasks WHERE status = 'active';
EXPLAIN QUERY PLAN SELECT * FROM tasks WHERE priority = 'high';
EXPLAIN QUERY PLAN SELECT * FROM tasks WHERE user_id = 1;
```
Assert query plan text includes index usage for each relevant query.

**Recommended Test Prioritization**

1. Must-have: NOT NULL, UNIQUE, CHECK bounds/enums, FK cascade, defaults.
2. Must-have: updated_at trigger behavior.
3. Should-have: schema drift checks via sqlite_master and PRAGMA.
4. Should-have: index usage query plan checks.
5. Decision test: due_date DB format gap (document current behavior vs desired policy).

If you want, I can generate a concrete pytest checklist mapped 1:1 to these SQL assertions in README.md style, ready to implement.