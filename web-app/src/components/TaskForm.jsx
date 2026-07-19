import React, { useState } from 'react';

// ============================================================
// TaskForm — the component referenced throughout Module 4 (Writer)
//
// The data-testid attributes below are the locators that Copilot
// reads when generating Playwright Page Objects. Open this file
// in VS Code BEFORE prompting Copilot to generate web tests
// (Module 4, Lab 14).
//
// Locators:
//   task-title      — title input
//   task-description— description textarea
//   task-due-date   — due date input
//   task-priority   — priority select
//   submit-btn      — submit button
//   cancel-btn      — cancel button
//   error-message   — validation error container
// ============================================================

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001';

export default function TaskForm({ onCreated, onCancel }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [priority, setPriority] = useState('medium');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    setError('');

    // Client-side validation (mirrors the API)
    if (!title.trim()) {
      setError('Title is required');
      return;
    }
    if (title.length > 200) {
      setError('Title must not exceed 200 characters');
      return;
    }

    setSubmitting(true);
    try {
      const res = await fetch(`${API_BASE_URL}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: title.trim(),
          description: description.trim() || null,
          due_date: dueDate || null,
          priority,
        }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        setError(data.error || 'Failed to create task');
        setSubmitting(false);
        return;
      }
      const task = await res.json();
      // Reset form
      setTitle('');
      setDescription('');
      setDueDate('');
      setPriority('medium');
      setSubmitting(false);
      if (onCreated) onCreated(task);
    } catch (e) {
      setError('Network error — could not reach the API');
      setSubmitting(false);
    }
  };

  return (
    <div className="task-form" data-testid="task-form">
      <h2>New Task</h2>

      {error && (
        <div className="error-message" data-testid="error-message" role="alert">
          {error}
        </div>
      )}

      <label htmlFor="title">Title</label>
      <input
        id="title"
        type="text"
        data-testid="task-title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="What needs doing?"
        maxLength={250}
      />

      <label htmlFor="description">Description</label>
      <textarea
        id="description"
        data-testid="task-description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Optional details"
        rows={3}
      />

      <label htmlFor="due-date">Due date</label>
      <input
        id="due-date"
        type="date"
        data-testid="task-due-date"
        value={dueDate}
        onChange={(e) => setDueDate(e.target.value)}
      />

      <label htmlFor="priority">Priority</label>
      <select
        id="priority"
        data-testid="task-priority"
        value={priority}
        onChange={(e) => setPriority(e.target.value)}
      >
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
      </select>

      <div className="task-form-actions">
        <button
          type="button"
          data-testid="submit-btn"
          onClick={handleSubmit}
          disabled={submitting}
        >
          {submitting ? 'Creating…' : 'Create Task'}
        </button>
        <button
          type="button"
          data-testid="cancel-btn"
          onClick={onCancel}
        >
          Cancel
        </button>
      </div>
    </div>
  );
}
