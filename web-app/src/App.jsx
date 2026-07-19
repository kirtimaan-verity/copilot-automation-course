import React, { useState, useEffect, useCallback } from 'react';
import TaskForm from './components/TaskForm';
import TaskList from './components/TaskList';
import './App.css';

// ============================================================
// App — the root component. Referenced in Module 1 Lab 01/02
// ("explore the repository") and Module 4 (Writer).
// ============================================================

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001';

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [filter, setFilter] = useState('');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);

  const loadTasks = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filter) params.set('status', filter);
      if (search) params.set('search', search);
      const res = await fetch(`${API_BASE_URL}/tasks?${params.toString()}`);
      const data = await res.json();
      setTasks(Array.isArray(data) ? data : []);
    } catch (e) {
      setTasks([]);
    } finally {
      setLoading(false);
    }
  }, [filter, search]);

  useEffect(() => {
    // Debounce search by 300ms (Module 3 references this timing)
    const t = setTimeout(loadTasks, 300);
    return () => clearTimeout(t);
  }, [loadTasks]);

  const handleCreated = () => {
    setShowForm(false);
    loadTasks();
  };

  const handleDelete = async (id) => {
    await fetch(`${API_BASE_URL}/tasks/${id}`, { method: 'DELETE' });
    loadTasks();
  };

  return (
    <div className="app" data-testid="app-root">
      <header className="app-header">
        <h1>Task Manager</h1>
        <span className="app-subtitle">Copilot Automation Course — Demo App</span>
      </header>

      <main className="app-main">
        {showForm ? (
          <TaskForm onCreated={handleCreated} onCancel={() => setShowForm(false)} />
        ) : (
          <TaskList
            tasks={tasks}
            onNewTask={() => setShowForm(true)}
            onDelete={handleDelete}
            filter={filter}
            onFilterChange={setFilter}
            search={search}
            onSearchChange={setSearch}
          />
        )}
        {loading && <div className="app-loading" data-testid="loading">Loading…</div>}
      </main>
    </div>
  );
}
