# AgentTrace 🔍

> MCP server for tracing, logging, and debugging multi-agent systems — one session, full visibility.

---

## What is AgentTrace?

When something breaks in a multi-agent system, finding the root cause is painful. Logs are scattered across agents, tool calls are invisible, and there's no single place to see what actually happened.

**AgentTrace** solves this by treating a **session** as the source of truth. Every human input, agent-to-agent call, tool invocation, and human-in-the-loop event is captured under a single session — giving you a complete, queryable trace tree of everything that happened.

---

## Features

- 📌 **Session-scoped tracing** — every run is one session, all events hang off it
- 🌲 **Full trace tree reconstruction** — visualize the exact call graph via `parent_span_id`
- 🔎 **Cross-session querying** — query by agent, error type, span type, or time range across all sessions
- 🔁 **Soft session replay** — re-inject original inputs into a fresh run for root cause analysis, optionally starting from mid-trace
- 🧩 **Protocol-native** — built as an MCP server, any MCP-compatible agent gets tracing for free
- 🏗️ **Production-grade** — async SQLAlchemy, Postgres, strict three-layer architecture

---

## Span Types

| Type          | Description                                  |
| ------------- | -------------------------------------------- |
| `human_input` | A user message sent to the orchestrator      |
| `agent_call`  | One agent calling another agent              |
| `tool_call`   | An agent invoking an MCP tool                |
| `hitl`        | A human-in-the-loop review or approval event |

---

## MCP Tools

| Tool                  | Description                                         |
| --------------------- | --------------------------------------------------- |
| `create_session`      | Start a new trace session                           |
| `start_span`          | Open a new span inside a session                    |
| `end_span`            | Close a span with output and status                 |
| `log_event`           | Log a notable event inside a span                   |
| `query_session`       | Get the full trace tree for a session               |
| `query_cross_session` | Query spans/events across all sessions with filters |
| `replay_session`      | Replay a session's inputs into a new run            |

---

## Tech Stack

| Layer           | Technology         |
| --------------- | ------------------ |
| MCP Framework   | FastMCP            |
| Database        | PostgreSQL         |
| ORM             | SQLAlchemy (async) |
| Migrations      | Alembic            |
| Validation      | Pydantic           |
| Package Manager | UV                 |

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

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL
- UV

### Installation

```bash
# Clone the repo
git clone https://github.com/your-username/agenttrace.git
cd agenttrace

# Install dependencies
uv sync

# Copy env file
cp .env.example .env
```

### Configuration

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/agenttrace
```

### Run Migrations

```bash
alembic upgrade head
```

### Start the Server

```bash
uv run python -m mcp_tracer.server
```

---

## How It Works

```
Session abc-123
  ├── [human_input]  span-1   "Summarize this report"
  │     └── [agent_call]  span-2   Orchestrator → ResearchAgent
  │           ├── [tool_call]  span-3   ResearchAgent → web_search
  │           └── [tool_call]  span-4   ResearchAgent → read_file
  │                 └── EVENT: error — "file not found"   ← root cause
  └── [hitl]  span-5   pending approval
```

Every span carries a `parent_span_id`, allowing AgentTrace to reconstruct the full call tree from flat database rows — making root cause analysis fast and visual.

---

## Roadmap

### v1 (Current)

- [x] Session management
- [x] Span lifecycle tracking
- [x] Event logging
- [x] Trace tree reconstruction
- [x] Cross-session querying
- [x] Soft session replay

### v2 (Planned)

- [ ] Hard replay (snapshot + re-inject tool outputs)
- [ ] Visual DAG dashboard
- [ ] Log sampling and levels for production
- [ ] Session branching for retries
- [ ] Alerting hooks
- [ ] Agent confidence / anomaly scoring

---

## Contributing

Contributions are welcome! Please open an issue first to discuss what you'd like to change.

---

## License

MIT
