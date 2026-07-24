-- 1) Orphaned tasks: finds tasks whose user_id points to no existing users row.
-- Non-zero rows mean referential integrity is broken (tasks without a valid owner).
SELECT t.*
FROM tasks AS t
LEFT JOIN users AS u ON u.id = t.user_id
WHERE t.user_id IS NOT NULL
  AND u.id IS NULL;


-- 2) Past-due active tasks: finds tasks with due_date before today but still marked active.
-- Non-zero rows mean status is inconsistent (should likely be 'overdue').
SELECT t.*
FROM tasks AS t
WHERE t.due_date IS NOT NULL
  AND date(t.due_date) < date('now')
  AND t.status = 'active';


-- 3) Duplicate user emails: finds users that share the same email.
-- Non-zero rows mean UNIQUE email integrity has been violated.
SELECT u.*
FROM users AS u
WHERE u.email IN (
    SELECT email
    FROM users
    GROUP BY email
    HAVING COUNT(*) > 1
);


-- 4) Invalid task priority: finds tasks with priority outside (low, medium, high).
-- Non-zero rows mean invalid priority values exist.
SELECT t.*
FROM tasks AS t
WHERE t.priority IS NULL
   OR t.priority NOT IN ('low', 'medium', 'high');


-- 5) Invalid task status: finds tasks with status outside (active, completed, overdue).
-- Non-zero rows mean invalid or unexpected status values exist.
SELECT t.*
FROM tasks AS t
WHERE t.status IS NULL
   OR t.status NOT IN ('active', 'completed', 'overdue');