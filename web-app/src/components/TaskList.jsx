import React from 'react';

// ============================================================
// TaskList — displays tasks; referenced in Module 4 Lab 14
// (TaskListPage Page Object) and Module 8 Lab 32 (visual tests).
//
// Locators:
//   task-list       — the list container
//   task-card       — one card per task
//   task-card-title — the task title within a card
//   new-task-btn    — opens the task form
//   filter-status   — status filter select
//   search-input    — search box
// ============================================================

export default function TaskList({ tasks, onNewTask, onDelete, filter, onFilterChange, search, onSearchChange }) {
  return (
    <div className="task-list-panel">
      <div className="task-list-toolbar">
        <button data-testid="new-task-btn" onClick={onNewTask}>+ New Task</button>

        <input
          data-testid="search-input"
          type="text"
          placeholder="Search tasks…"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          maxLength={100}
        />

        <select
          data-testid="filter-status"
          value={filter}
          onChange={(e) => onFilterChange(e.target.value)}
        >
          <option value="">All statuses</option>
          <option value="active">Active</option>
          <option value="completed">Completed</option>
          <option value="overdue">Overdue</option>
          <option value="archived">Archived</option>
        </select>
      </div>

      <ul className="task-list" data-testid="task-list">
        {tasks.length === 0 && (
          <li className="task-empty" data-testid="task-empty">No tasks yet.</li>
        )}
        {tasks.map((task) => (
          <li
            key={task.id}
            className={`task-card priority-${task.priority} status-${task.status}`}
            data-testid="task-card"
            data-task-id={task.id}
          >
            <div className="task-card-main">
              <span className="task-card-title" data-testid="task-card-title">
                {task.title}
              </span>
              <span className={`task-badge priority-${task.priority}`}>
                {task.priority}
              </span>
              <span className={`task-badge status-${task.status}`}>
                {task.status}
              </span>
            </div>
            {task.due_date && (
              <div className="task-card-due">Due: {task.due_date}</div>
            )}
            <button
              className="task-delete-btn"
              data-testid="delete-btn"
              onClick={() => onDelete(task.id)}
              aria-label={`Delete ${task.title}`}
            >
              ×
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
