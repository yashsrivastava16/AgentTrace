# AgentTrace 🔍

> MCP server for tracing, logging, and debugging multi-agent systems — one session, full visibility.

---

## What is AgentTrace?

When something breaks in a multi-agent system, finding the root cause is painful. Logs are scattered across agents, tool calls are invisible, and there's no single place to see what actually happened.

**AgentTrace** solves this by treating a **session** as the source of truth. Every human input, agent-to-agent call, tool invocation, and human-in-the-loop event is captured under a single session — giving you a complete, queryable trace tree of everything that happened.

```
Session abc-123
  ├── [human_input]  span-1   "Summarize this report"
  │     └── [agent_call]  span-2   Orchestrator → ResearchAgent
  │           ├── [tool_call]  span-3   ResearchAgent → web_search
  │           └── [tool_call]  span-4   ResearchAgent → read_file
  │                 └── EVENT: error — "file not found"   ← root cause
  └── [hitl]  span-5   pending approval
```

---

🔒 **Need Advanced Authorization?**

> As an MCP server, AgentTrace acts as the central hub for your multi-agent architecture. If your setup requires strict access controls, granular agent permissions, or specialized authorization flows, check out the `feature/Auth-Enable` branch for our fully authenticated implementation!

---

## Features

- 📌 **Session-scoped tracing** — every run is one session, all events hang off it
- 🌲 **Full trace tree reconstruction** — visualize the exact call graph via `parent_span_id`
- 🔎 **Cross-session querying** — query by agent, error type, span type, or time range across all sessions
- 🔁 **Soft session replay** — re-inject original inputs into a fresh run for root cause analysis, optionally starting from mid-trace
- 🧩 **Protocol-native** — built as an MCP server, any MCP-compatible agent gets tracing for free just by connecting
- 🏗️ **Production-grade** — async SQLAlchemy, PostgreSQL, strict three-layer architecture

---

## Tech Stack

| Layer           | Technology                   |
| --------------- | ---------------------------- |
| MCP Framework   | FastMCP 3.x                  |
| Database        | PostgreSQL 16                |
| ORM             | SQLAlchemy (async)           |
| Migrations      | Alembic                      |
| Validation      | Pydantic + pydantic-settings |
| Package Manager | UV                           |

---

## Setup

### Option 1 — Run Locally

**Prerequisites:** Python 3.11+, PostgreSQL, UV

```bash
# Clone the repo
git clone https://github.com/your-username/agenttrace.git
cd agenttrace

# Install dependencies
uv sync

# Copy and configure env
cp .env.example .env
```

Edit `.env`:

```env
APP_ENV=development
DEBUG=false
HOST=0.0.0.0
PORT=8000
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/agenttrace
```

Run migrations and start the server:

```bash
alembic upgrade head
python -m mcp_tracer.server
```

Server runs at `http://localhost:8000/mcp`

---

### Option 2 — Run with Docker (Recommended)

**Prerequisites:** Docker, Docker Compose

```bash
git clone https://github.com/your-username/agenttrace.git
cd agenttrace

docker compose -f docker/docker-compose.yml up --build
```

That's it. Docker will spin up PostgreSQL, wait for it to be healthy, run migrations automatically, and start the MCP server on port `8000`.

Server runs at `http://localhost:8000/mcp`

---

### Connect to VS Code

Once the server is running, add this to your VS Code MCP settings (`Ctrl+Shift+P` → `Claude: Open MCP Settings`):

```json
{
  "mcpServers": {
    "agenttrace": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

Refresh MCP servers and AgentTrace will appear with all 7 tools available.

---

### Connect to Any MCP-Compatible Agent

```python
from fastmcp import Client

async with Client("http://localhost:8000/mcp") as client:
    tools = await client.list_tools()
    print(tools)  # lists all 7 AgentTrace tools
```

---

## How It Works

AgentTrace uses three core concepts:

**Session** — the top-level container for a single run. Everything belongs to a session.

**Span** — a single unit of work inside a session. One agent calling another is one span. A human sending input is one span. Each span has a `parent_span_id` which is how AgentTrace builds the trace tree.

**Event** — something notable that happened inside a span. An error, a warning, or a log message.

### Span Types

| Type          | When to use                                |
| ------------- | ------------------------------------------ |
| `human_input` | A user sends a message to the system       |
| `agent_call`  | One agent calls another agent              |
| `tool_call`   | An agent invokes an MCP tool               |
| `hitl`        | System pauses for human-in-the-loop review |

---

## Tools Reference

### `create_session`

Creates a new trace session. Call this at the start of every agent run.

**Parameters:**

| Parameter  | Type   | Required | Description                                  |
| ---------- | ------ | -------- | -------------------------------------------- |
| `name`     | string | ✅       | Human readable name for this run             |
| `metadata` | dict   | ❌       | Optional key-value context e.g. env, version |

**Returns:** `session_id`, `name`, `status`, `started_at`, `metadata`

**Example:**

```python
session = await client.call_tool("create_session", {
    "name": "invoice-processing-run-42",
    "metadata": {
        "env": "production",
        "triggered_by": "scheduler",
        "version": "1.0.0"
    }
})
session_id = session["session_id"]
```

---

### `start_span`

Opens a new span inside a session. Call this every time an agent starts a unit of work.

**Parameters:**

| Parameter        | Type   | Required | Description                                             |
| ---------------- | ------ | -------- | ------------------------------------------------------- |
| `session_id`     | string | ✅       | UUID of the parent session                              |
| `span_type`      | string | ✅       | One of `human_input`, `agent_call`, `tool_call`, `hitl` |
| `actor`          | string | ✅       | Who initiated — agent name or `"human"`                 |
| `target`         | string | ✅       | Who received — agent name or tool name                  |
| `input`          | dict   | ❌       | Payload sent to the target                              |
| `parent_span_id` | string | ❌       | UUID of parent span for nested calls                    |

**Returns:** `span_id`, `session_id`, `parent_span_id`, `span_type`, `actor`, `target`, `status`, `started_at`

**Example:**

```python
# Top level span — human sends input
span1 = await client.call_tool("start_span", {
    "session_id": session_id,
    "span_type": "human_input",
    "actor": "human",
    "target": "orchestrator",
    "input": {"message": "Process the invoice batch"}
})

# Child span — orchestrator calls an agent
span2 = await client.call_tool("start_span", {
    "session_id": session_id,
    "span_type": "agent_call",
    "actor": "orchestrator",
    "target": "invoice_agent",
    "input": {"batch_id": "batch-99"},
    "parent_span_id": span1["span_id"]   # nested under span1
})
```

---

### `end_span`

Closes a span and records its output. Always call this when a unit of work finishes — success or failure.

**Parameters:**

| Parameter | Type   | Required | Description                      |
| --------- | ------ | -------- | -------------------------------- |
| `span_id` | string | ✅       | UUID of the span to close        |
| `status`  | string | ✅       | `"success"` or `"failed"`        |
| `output`  | dict   | ❌       | Payload returned from the target |

**Returns:** `span_id`, `status`, `ended_at`, `output`

**Example:**

```python
# End successfully
await client.call_tool("end_span", {
    "span_id": span2["span_id"],
    "status": "success",
    "output": {"invoices_processed": 42}
})

# End with failure
await client.call_tool("end_span", {
    "span_id": span2["span_id"],
    "status": "failed",
    "output": {"error": "Batch not found"}
})
```

---

### `log_event`

Logs a notable event inside a span. Use this for errors, warnings, or anything worth capturing mid-span.

**Parameters:**

| Parameter    | Type   | Required | Description                            |
| ------------ | ------ | -------- | -------------------------------------- |
| `span_id`    | string | ✅       | UUID of the span this event belongs to |
| `event_type` | string | ✅       | One of `log`, `error`, `warning`       |
| `message`    | string | ✅       | Human readable description             |
| `metadata`   | dict   | ❌       | Additional structured context          |

**Returns:** `event_id`, `span_id`, `event_type`, `message`, `created_at`

**Example:**

```python
# Log an error
await client.call_tool("log_event", {
    "span_id": span2["span_id"],
    "event_type": "error",
    "message": "Invoice file not found on S3",
    "metadata": {
        "bucket": "invoices-prod",
        "key": "batch-99/invoice.pdf",
        "http_status": 404
    }
})

# Log a warning
await client.call_tool("log_event", {
    "span_id": span2["span_id"],
    "event_type": "warning",
    "message": "Retrying after rate limit",
    "metadata": {"retry_attempt": 2, "wait_seconds": 5}
})
```

---

### `complete_session` / `fail_session`

Marks a session as completed or failed. Call one of these when the entire run finishes.

**Parameters:**

| Parameter    | Type   | Required | Description                  |
| ------------ | ------ | -------- | ---------------------------- |
| `session_id` | string | ✅       | UUID of the session to close |

**Example:**

```python
# On success
await client.call_tool("complete_session", {"session_id": session_id})

# On failure
await client.call_tool("fail_session", {"session_id": session_id})
```

---

### `query_session`

Retrieves the full nested trace tree for a session. This is your primary debugging tool — one call gives you everything that happened in a run.

**Parameters:**

| Parameter    | Type   | Required | Description                     |
| ------------ | ------ | -------- | ------------------------------- |
| `session_id` | string | ✅       | UUID of the session to retrieve |

**Returns:** Full nested trace with all spans and events

**Example:**

```python
trace = await client.call_tool("query_session", {
    "session_id": session_id
})

# Response structure:
# {
#   "session_id": "abc-123",
#   "name": "invoice-processing-run-42",
#   "status": "failed",
#   "spans": [
#     {
#       "span_id": "...",
#       "span_type": "human_input",
#       "actor": "human",
#       "target": "orchestrator",
#       "status": "failed",
#       "events": [],
#       "children": [
#         {
#           "span_id": "...",
#           "span_type": "agent_call",
#           "status": "failed",
#           "events": [
#             {
#               "event_type": "error",
#               "message": "Invoice file not found on S3"
#             }
#           ],
#           "children": []
#         }
#       ]
#     }
#   ]
# }
```

---

### `query_cross_session`

Queries spans across all sessions with filters. Use this to find recurring failures, slow agents, or patterns across multiple runs.

**Parameters:**

| Parameter        | Type   | Required | Description                                                         |
| ---------------- | ------ | -------- | ------------------------------------------------------------------- |
| `actor`          | string | ❌       | Filter by actor name e.g. `"invoice_agent"`                         |
| `span_type`      | string | ❌       | Filter by type — `human_input`, `agent_call`, `tool_call`, `hitl`   |
| `status`         | string | ❌       | Filter by status — `running`, `success`, `failed`                   |
| `event_type`     | string | ❌       | Filter spans containing this event type — `log`, `error`, `warning` |
| `started_after`  | string | ❌       | ISO datetime e.g. `"2026-01-01T00:00:00"`                           |
| `started_before` | string | ❌       | ISO datetime e.g. `"2026-12-31T23:59:59"`                           |

**Returns:** List of matching spans with session context and events

**Example:**

```python
# Find all failed spans from invoice_agent this week
results = await client.call_tool("query_cross_session", {
    "actor": "invoice_agent",
    "status": "failed",
    "started_after": "2026-03-17T00:00:00"
})

# Find all spans that had an error event
results = await client.call_tool("query_cross_session", {
    "event_type": "error"
})

# Find all tool_call spans that failed
results = await client.call_tool("query_cross_session", {
    "span_type": "tool_call",
    "status": "failed"
})
```

---

### `replay_session`

Creates a new session and returns all original inputs from a past session so agents can re-execute them fresh. Useful for reproducing bugs without manually re-running the entire system.

**Parameters:**

| Parameter      | Type   | Required | Description                                                                      |
| -------------- | ------ | -------- | -------------------------------------------------------------------------------- |
| `session_id`   | string | ✅       | UUID of the session to replay                                                    |
| `from_span_id` | string | ❌       | Start replay from a specific span — useful to re-run only from the failure point |

**Returns:** `new_session_id`, `replayed_from_session_id`, `spans_to_replay`

**Example:**

```python
# Full replay from the beginning
replay = await client.call_tool("replay_session", {
    "session_id": session_id
})

# Partial replay — start from the failure point
replay = await client.call_tool("replay_session", {
    "session_id": session_id,
    "from_span_id": failed_span_id
})

# Feed inputs back to your agents using the new session
new_session_id = replay["new_session_id"]
for span in replay["spans_to_replay"]:
    await your_agent.run(span["input"], session_id=new_session_id)
```

---

## Full Integration Example

Complete example showing how to wrap an existing multi-agent system with AgentTrace:

```python
import asyncio
from fastmcp import Client

AGENTTRACE_URL = "http://localhost:8000/mcp"


async def run_pipeline(user_message: str):
    async with Client(AGENTTRACE_URL) as tracer:

        # 1. Start session
        session = await tracer.call_tool("create_session", {
            "name": "pipeline-run",
            "metadata": {"triggered_by": "api"}
        })
        session_id = session["session_id"]

        try:
            # 2. Trace human input
            root_span = await tracer.call_tool("start_span", {
                "session_id": session_id,
                "span_type": "human_input",
                "actor": "human",
                "target": "orchestrator",
                "input": {"message": user_message}
            })

            # 3. Trace orchestrator → agent call
            agent_span = await tracer.call_tool("start_span", {
                "session_id": session_id,
                "span_type": "agent_call",
                "actor": "orchestrator",
                "target": "research_agent",
                "input": {"task": user_message},
                "parent_span_id": root_span["span_id"]
            })

            try:
                # Your actual agent logic here
                result = await research_agent.run(user_message)

                await tracer.call_tool("end_span", {
                    "span_id": agent_span["span_id"],
                    "status": "success",
                    "output": {"result": result}
                })

            except Exception as e:
                await tracer.call_tool("log_event", {
                    "span_id": agent_span["span_id"],
                    "event_type": "error",
                    "message": str(e),
                    "metadata": {"exception_type": type(e).__name__}
                })
                await tracer.call_tool("end_span", {
                    "span_id": agent_span["span_id"],
                    "status": "failed"
                })
                raise

            # 4. Close root span and complete session
            await tracer.call_tool("end_span", {
                "span_id": root_span["span_id"],
                "status": "success"
            })
            await tracer.call_tool("complete_session", {
                "session_id": session_id
            })

        except Exception:
            await tracer.call_tool("fail_session", {"session_id": session_id})
            raise


asyncio.run(run_pipeline("Summarize the quarterly report"))
```

---

## Query Examples

### Debugging a Specific Run

**Scenario:** A user-reported issue with invoice processing. You remember the session ID from the error logs.

```python
# Get the full trace tree to understand what went wrong
trace = await tracer.call_tool("query_session", {
    "session_id": "69f4f019-b5ca-46a2-bf5e-59fb176c3227"
})

# Output shows the entire call chain with errors
# Navigate to the failed span and see exactly where it broke
```

### Find All Errors This Week

**Scenario:** You want to see all errors across your system in the last 7 days.

```python
results = await tracer.call_tool("query_cross_session", {
    "event_type": "error",
    "started_after": "2026-03-17T00:00:00",
    "started_before": "2026-03-24T23:59:59"
})

# Returns all spans containing error events — useful for weekly reviews
```

### Spot Failing Agents

**Scenario:** The `invoice_agent` has been failing. Find all its failures.

```python
results = await tracer.call_tool("query_cross_session", {
    "actor": "invoice_agent",
    "status": "failed"
})

# See every failed run from this agent — identify patterns
```

### Find Slow Tool Calls

**Scenario:** Tool calls are taking too long. Find all tool calls that might be problematic.

```python
results = await tracer.call_tool("query_cross_session", {
    "span_type": "tool_call",
    "status": "success"
})

# Returns all successful tool calls — you can inspect duration and optimize
```

### Reproduce a Bug

**Scenario:** A user reports a bug. Replay the session to debug locally.

```python
# Find the failed session
failed_session = await tracer.call_tool("query_cross_session", {
    "actor": "research_agent",
    "status": "failed",
    "started_after": "2026-03-24T12:00:00"
})

session_id = failed_session[0]["session_id"]

# Replay it in a fresh session with new logic
replay = await tracer.call_tool("replay_session", {
    "session_id": session_id
})

new_session = replay["new_session_id"]
# Re-run your pipeline with the new session ID — same inputs, fresh code
```

### Find All Pending HITL Reviews

**Scenario:** You want to see all human-in-the-loop approvals that are still pending.

```python
results = await tracer.call_tool("query_cross_session", {
    "span_type": "hitl",
    "status": "running"
})

# See all pending approvals across all sessions
```

### Cross-Session Pattern Analysis

**Scenario:** Analyze all agent-to-agent calls to identify bottlenecks.

```python
results = await tracer.call_tool("query_cross_session", {
    "span_type": "agent_call"
})

# Returns all inter-agent calls — analyze metrics like success rate, frequency
for span in results:
    print(f"{span['actor']} → {span['target']}: {span['status']}")
```

---

## Project Structure

```
mcp-tracer/
├── src/
│   └── mcp_tracer/
│       ├── server.py           # FastMCP entry point
│       ├── tools/              # MCP tool handlers
│       ├── db/                 # Models + repositories
│       ├── schemas/            # Pydantic I/O schemas
│       ├── services/           # Business logic
│       └── core/               # Config, logging, exceptions
├── migrations/                 # Alembic migrations
├── tests/
└── docker/
```

---

## Roadmap

### v1 (Current)

- [x] Session lifecycle management
- [x] Span tracking with parent-child nesting
- [x] Event logging
- [x] Full trace tree reconstruction
- [x] Cross-session querying with filters
- [x] Soft session replay

### v2 (Planned)

- [ ] Hard replay — snapshot and re-inject tool outputs for identical reproduction
- [ ] Visual DAG dashboard
- [ ] Log sampling and levels for production
- [ ] Session branching for retries
- [ ] Alerting hooks
- [ ] Agent confidence and anomaly scoring

---

## Contributing

First off, thank you for considering contributing to #AgnetTrace! It's people like you that make the open-source community such an amazing place to learn, inspire, and create.

We welcome contributions of all kinds, whether it is fixing bugs, improving documentation, suggesting new features, or writing code.

---

## ⚖️ License and Contributions

This project is open-source and released under the **MIT License**. By contributing to this repository, you agree that your contributions will be licensed under its MIT License.

---

## 🚀 How Can I Contribute?

### Reporting Bugs

If you find a bug, please create an issue to report it. To help us resolve it quickly, include:

- A clear and descriptive title.
- Steps to reproduce the exact behavior.
- Expected behavior versus what actually happened.
- Your operating system, browser, and relevant version numbers.

### Suggesting Enhancements

Feature requests are always welcome! When proposing a new feature, please open an issue and include:

- The problem this feature solves.
- A detailed description of the proposed solution.
- Any alternative solutions you have considered.
- Mockups or code snippets if applicable.

---

## 🛠️ Pull Request Process

When you are ready to submit your code, follow this process:

1. Create a new branch for your feature or bugfix: `git checkout -b feature/your-feature-name`
2. Make your changes and test them thoroughly.
3. Commit your changes with clear, descriptive commit messages.
4. Push your branch to your forked repository: `git push origin feature/your-feature-name`
5. Open a Pull Request (PR) against the `feature/External-PR` branch of the original repository.
6. Provide a detailed description in your PR explaining what changes you made and why.

A maintainer will review your PR, provide feedback, and merge it once it is approved.

---

## 🤝 Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project, you agree to abide by its terms. We expect all contributors to maintain a respectful and welcoming environment for everyone.
