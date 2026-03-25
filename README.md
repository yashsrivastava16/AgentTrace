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

## Features

- 📌 **Session-scoped tracing** — every run is one session, all events hang off it
- 🌲 **Full trace tree reconstruction** — visualize the exact call graph via `parent_span_id`
- 🔎 **Cross-session querying** — query by agent, error type, span type, or time range across all sessions
- 🔁 **Soft session replay** — re-inject original inputs into a fresh run for root cause analysis, optionally starting from mid-trace
- 🔐 **JWT authentication** — agent-level and session-scoped tokens for secure multi-agent access
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
| Auth            | python-jose + JWT            |
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

# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=43200
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
```

Add your JWT secret to `.env`:

```env
JWT_SECRET_KEY=your-secret-key-here
```

Generate a secret if you don't have one:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Start everything:

```bash
docker compose -f docker/docker-compose.yml up --build
```

Docker will spin up PostgreSQL, wait for it to be healthy, run migrations automatically, and start the MCP server on port `8000`.

Server runs at `http://localhost:8000/mcp`

---

## Authentication

AgentTrace uses JWT Bearer token authentication. Every tool call must include a valid token in the `Authorization` header.

### Two Token Types

| Token Type        | Purpose                                                               | Scope                      |
| ----------------- | --------------------------------------------------------------------- | -------------------------- |
| **Agent Token**   | General access — used to call `create_session` and get a `session_id` | Not session-scoped         |
| **Session Token** | Locked to a specific session — used for all calls within that session | Scoped to one `session_id` |

---

### Generate an Agent Token

**Via Docker:**

```bash
docker compose exec app python -c "
import sys
sys.path.insert(0, 'src')
from mcp_tracer.core.security import create_agent_token
print(create_agent_token('my-agent'))
"
```

**Via script (`scripts/generate_token.py`):**

```python
import sys, os
sys.path.insert(0, "src")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://placeholder")

from mcp_tracer.core.security import create_agent_token, create_session_token

# Agent token — general purpose
print(create_agent_token("my-agent"))

# Session token — scoped to a specific session (use after create_session)
# print(create_session_token("my-agent", "your-session-uuid-here"))
```

```bash
uv run python scripts/generate_token.py
```

Output will look like:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJteS1hZ2VudCIsInRva2VuX3R5cGUiOiJhZ2VudCJ9...
```

---

### Token Flow in Production

```
1. Agent starts
   → uses agent_token to call create_session
   → receives session_id

2. Agent generates session_token scoped to that session_id
   → create_session_token("my-agent", session_id)

3. Agent uses session_token for all remaining calls
   → start_span, end_span, log_event, query_session, replay_session

4. New run → repeat from step 1
```

In code:

```python
from fastmcp import Client
from mcp_tracer.core.security import create_agent_token, create_session_token

agent_token = create_agent_token("my-agent")

# Step 1 — create session with agent token
async with Client("http://localhost:8000/mcp",
                  headers={"Authorization": f"Bearer {agent_token}"}) as client:
    session = await client.call_tool("create_session", {"name": "my-run"})
    session_id = session["session_id"]

# Step 2 — generate session token
session_token = create_session_token("my-agent", session_id)

# Step 3 — use session token for all remaining calls
async with Client("http://localhost:8000/mcp",
                  headers={"Authorization": f"Bearer {session_token}"}) as client:
    await client.call_tool("start_span", {
        "session_id": session_id,
        "span_type": "agent_call",
        "actor": "orchestrator",
        "target": "research_agent",
        "input": {"task": "summarize report"}
    })
```

---

### Connect to VS Code

Generate an agent token (see above), then add it to your MCP settings (`Ctrl+Shift+P` → `Claude: Open MCP Settings`):

```json
{
  "mcpServers": {
    "agenttrace": {
      "type": "http",
      "url": "http://localhost:8000/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_AGENT_TOKEN_HERE"
      }
    }
  }
}
```

> **Note:** VS Code uses a static config so agent token is used for all tools in dev. Session-scoped tokens apply to production agents that manage their own auth lifecycle programmatically.

---

### Connect to Any MCP-Compatible Agent

```python
from fastmcp import Client

async with Client(
    "http://localhost:8000/mcp",
    headers={"Authorization": f"Bearer {agent_token}"}
) as client:
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

Creates a new trace session. Call this at the start of every agent run. Requires **agent token**.

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
    "parent_span_id": span1["span_id"]
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
await client.call_tool("complete_session", {"session_id": session_id})
await client.call_tool("fail_session", {"session_id": session_id})
```

---

### `query_session`

Retrieves the full nested trace tree for a session. One call gives you everything that happened in a run.

**Parameters:**

| Parameter    | Type   | Required | Description                     |
| ------------ | ------ | -------- | ------------------------------- |
| `session_id` | string | ✅       | UUID of the session to retrieve |

**Returns:** Full nested trace with all spans and events

**Example:**

```python
trace = await client.call_tool("query_session", {"session_id": session_id})

# {
#   "session_id": "abc-123",
#   "name": "invoice-processing-run-42",
#   "status": "failed",
#   "spans": [
#     {
#       "span_type": "human_input",
#       "status": "failed",
#       "events": [],
#       "children": [
#         {
#           "span_type": "agent_call",
#           "status": "failed",
#           "events": [{"event_type": "error", "message": "File not found"}],
#           "children": []
#         }
#       ]
#     }
#   ]
# }
```

---

### `query_cross_session`

Queries spans across all sessions with filters. Use this to find recurring failures or patterns. Requires **agent token**.

**Parameters:**

| Parameter        | Type   | Required | Description                                             |
| ---------------- | ------ | -------- | ------------------------------------------------------- |
| `actor`          | string | ❌       | Filter by actor name e.g. `"invoice_agent"`             |
| `span_type`      | string | ❌       | One of `human_input`, `agent_call`, `tool_call`, `hitl` |
| `status`         | string | ❌       | One of `running`, `success`, `failed`                   |
| `event_type`     | string | ❌       | Filter spans containing this event type                 |
| `started_after`  | string | ❌       | ISO datetime e.g. `"2026-01-01T00:00:00"`               |
| `started_before` | string | ❌       | ISO datetime e.g. `"2026-12-31T23:59:59"`               |

**Example:**

```python
# All failed spans from invoice_agent this week
results = await client.call_tool("query_cross_session", {
    "actor": "invoice_agent",
    "status": "failed",
    "started_after": "2026-03-17T00:00:00"
})

# All spans with error events
results = await client.call_tool("query_cross_session", {
    "event_type": "error"
})
```

---

### `replay_session`

Creates a new session and returns original inputs so agents can re-execute them fresh.

**Parameters:**

| Parameter      | Type   | Required | Description                       |
| -------------- | ------ | -------- | --------------------------------- |
| `session_id`   | string | ✅       | UUID of the session to replay     |
| `from_span_id` | string | ❌       | Start replay from a specific span |

**Example:**

```python
# Replay from the failure point
replay = await client.call_tool("replay_session", {
    "session_id": session_id,
    "from_span_id": failed_span_id
})

new_session_id = replay["new_session_id"]
for span in replay["spans_to_replay"]:
    await your_agent.run(span["input"], session_id=new_session_id)
```

---

## Full Integration Example

```python
import asyncio
from fastmcp import Client
from mcp_tracer.core.security import create_agent_token, create_session_token

AGENTTRACE_URL = "http://localhost:8000/mcp"


async def run_pipeline(user_message: str):
    agent_token = create_agent_token("orchestrator")

    # Step 1 — create session with agent token
    async with Client(AGENTTRACE_URL,
                      headers={"Authorization": f"Bearer {agent_token}"}) as client:
        session = await client.call_tool("create_session", {
            "name": "pipeline-run",
            "metadata": {"triggered_by": "api"}
        })
        session_id = session["session_id"]

    # Step 2 — generate session token
    session_token = create_session_token("orchestrator", session_id)

    # Step 3 — use session token for all remaining calls
    async with Client(AGENTTRACE_URL,
                      headers={"Authorization": f"Bearer {session_token}"}) as client:
        try:
            root_span = await client.call_tool("start_span", {
                "session_id": session_id,
                "span_type": "human_input",
                "actor": "human",
                "target": "orchestrator",
                "input": {"message": user_message}
            })

            agent_span = await client.call_tool("start_span", {
                "session_id": session_id,
                "span_type": "agent_call",
                "actor": "orchestrator",
                "target": "research_agent",
                "input": {"task": user_message},
                "parent_span_id": root_span["span_id"]
            })

            try:
                result = await research_agent.run(user_message)
                await client.call_tool("end_span", {
                    "span_id": agent_span["span_id"],
                    "status": "success",
                    "output": {"result": result}
                })

            except Exception as e:
                await client.call_tool("log_event", {
                    "span_id": agent_span["span_id"],
                    "event_type": "error",
                    "message": str(e),
                    "metadata": {"exception_type": type(e).__name__}
                })
                await client.call_tool("end_span", {
                    "span_id": agent_span["span_id"],
                    "status": "failed"
                })
                raise

            await client.call_tool("end_span", {
                "span_id": root_span["span_id"],
                "status": "success"
            })
            await client.call_tool("complete_session", {"session_id": session_id})

        except Exception:
            await client.call_tool("fail_session", {"session_id": session_id})
            raise


asyncio.run(run_pipeline("Summarize the quarterly report"))
```

---

## Query Examples

### Debug a Specific Run

```python
trace = await client.call_tool("query_session", {
    "session_id": "69f4f019-b5ca-46a2-bf5e-59fb176c3227"
})
```

### Find All Errors This Week

```python
results = await client.call_tool("query_cross_session", {
    "event_type": "error",
    "started_after": "2026-03-17T00:00:00"
})
```

### Spot a Failing Agent

```python
results = await client.call_tool("query_cross_session", {
    "actor": "invoice_agent",
    "status": "failed"
})
```

### Find Pending HITL Reviews

```python
results = await client.call_tool("query_cross_session", {
    "span_type": "hitl",
    "status": "running"
})
```

### Reproduce a Bug

```python
failed = await client.call_tool("query_cross_session", {
    "status": "failed",
    "started_after": "2026-03-24T12:00:00"
})

replay = await client.call_tool("replay_session", {
    "session_id": failed[0]["session_id"]
})
```

---

## Project Structure

```
mcp-tracer/
├── src/
│   └── mcp_tracer/
│       ├── server.py           # FastMCP entry point + JWT middleware
│       ├── tools/              # MCP tool handlers
│       ├── db/                 # Models + repositories
│       ├── schemas/            # Pydantic I/O schemas
│       ├── services/           # Business logic
│       └── core/
│           ├── config.py       # pydantic-settings
│           ├── security.py     # JWT token creation + verification
│           ├── lifespan.py     # startup + shutdown
│           └── logging.py      # structured logger
├── migrations/                 # Alembic migrations
├── scripts/
│   └── generate_token.py       # token generation utility
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
- [x] JWT authentication — agent and session-scoped tokens

### v2 (Planned)

- [ ] Automatic context propagation between agents
- [ ] Hard replay — snapshot and re-inject tool outputs
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
