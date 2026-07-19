// ============================================================
// Task Manager API server
// Start: node api/server.js
// Health check: curl http://localhost:3001/health
//
// Referenced across all modules as the API under test.
// Default port 3001 (override with PORT env var).
// ============================================================

const express = require('express');
const cors = require('cors');
const tasksRouter = require('./routes/tasks');

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// Health endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'task-manager-api', time: new Date().toISOString() });
});

// Routes
app.use('/tasks', tasksRouter);

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Not found' });
});

// Error handler — never leak stack traces (Module 9 security tests check this)
app.use((err, req, res, next) => {
  res.status(500).json({ error: 'Internal server error' });
});

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Task Manager API listening on http://localhost:${PORT}`);
  });
  // Graceful shutdown: lets Node flush V8 coverage (NODE_V8_COVERAGE)
  // when the server is stopped with kill/Ctrl+C — used in Module 7 Lab 28.
  process.on('SIGTERM', () => process.exit(0));
  process.on('SIGINT', () => process.exit(0));
}

module.exports = app;
