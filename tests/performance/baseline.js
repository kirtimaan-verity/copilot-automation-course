import http from "k6/http";
import { check, sleep } from "k6";

const BASE_URL = __ENV.API_BASE_URL || "http://localhost:3000";
const RUN_TAG_PREFIX = "k6-baseline";

// Per-VU cache of created task IDs used for DELETE operations during the run.
const createdTaskIds = [];

export const options = {
  scenarios: {
    baseline_mix: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "10s", target: 10 },
        { duration: "40s", target: 10 },
        { duration: "10s", target: 0 },
      ],
      gracefulRampDown: "0s",
    },
  },
  thresholds: {
    http_req_duration: ["p(95)<3"],
    http_req_failed: ["rate<0.01"],
  },
};

export function setup() {
  const runTag = `${RUN_TAG_PREFIX}-${Date.now()}`;
  return { runTag };
}

function createTask(runTag) {
  const payload = JSON.stringify({
    title: `${runTag}-vu${__VU}-iter${__ITER}`,
    description: "Created by k6 baseline load test",
    priority: "medium",
    status: "active",
  });

  const res = http.post(`${BASE_URL}/tasks`, payload, {
    headers: { "Content-Type": "application/json" },
    tags: { endpoint: "POST /tasks" },
  });

  check(res, {
    "POST /tasks status is 201": (r) => r.status === 201,
    "POST /tasks returns task id": (r) => {
      try {
        const body = r.json();
        return body && Number.isInteger(body.id);
      } catch (_err) {
        return false;
      }
    },
  });

  if (res.status === 201) {
    try {
      const body = res.json();
      if (body && Number.isInteger(body.id)) {
        createdTaskIds.push(body.id);
      }
    } catch (_err) {
      // Ignore parse errors; checks already capture response validity.
    }
  }
}

function getTasks() {
  const res = http.get(`${BASE_URL}/tasks`, {
    tags: { endpoint: "GET /tasks" },
  });

  check(res, {
    "GET /tasks status is 200": (r) => r.status === 200,
  });
}

function deleteTaskById(taskId) {
  const res = http.del(`${BASE_URL}/tasks/${taskId}`, null, {
    tags: { endpoint: "DELETE /tasks/{id}" },
  });

  check(res, {
    "DELETE /tasks/{id} status is 204 or 404": (r) => r.status === 204 || r.status === 404,
  });
}

export default function (data) {
  const roll = Math.random();

  if (roll < 0.7) {
    getTasks();
  } else if (roll < 0.9) {
    createTask(data.runTag);
  } else if (createdTaskIds.length > 0) {
    const taskId = createdTaskIds.pop();
    deleteTaskById(taskId);
  } else {
    // If there is nothing to delete yet, fall back to GET to avoid artificial failures.
    getTasks();
  }

  sleep(0.5);
}

export function teardown(data) {
  const listRes = http.get(`${BASE_URL}/tasks`, {
    tags: { endpoint: "TEARDOWN GET /tasks" },
  });

  check(listRes, {
    "teardown GET /tasks status is 200": (r) => r.status === 200,
  });

  if (listRes.status !== 200) {
    return;
  }

  let tasks = [];
  try {
    tasks = listRes.json();
  } catch (_err) {
    return;
  }

  if (!Array.isArray(tasks)) {
    return;
  }

  const createdByThisRun = tasks.filter((task) => {
    return task && typeof task.title === "string" && task.title.startsWith(data.runTag);
  });

  for (const task of createdByThisRun) {
    if (!Number.isInteger(task.id)) {
      continue;
    }

    const delRes = http.del(`${BASE_URL}/tasks/${task.id}`, null, {
      tags: { endpoint: "TEARDOWN DELETE /tasks/{id}" },
    });

    check(delRes, {
      "teardown DELETE /tasks/{id} status is 204 or 404": (r) => r.status === 204 || r.status === 404,
    });
  }
}

/*
Run command with JSON output:
k6 run -e API_BASE_URL=http://localhost:3000 --out json=results/k6-baseline.json tests/performance/baseline.js
*/
