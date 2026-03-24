"""
FastMCP application entry point.
Initializes the MCP server, registers all tools, and starts the server.
"""
from fastmcp import FastMCP

from mcp_tracer.core.config import settings
from mcp_tracer.db.engine import get_db
from mcp_tracer.tools import (
    register_session_tools,
    register_span_tools,
    register_event_tools,
    register_query_tools,
    register_replay_tools,
)

# Initialize FastMCP app
app = FastMCP(settings.APP_NAME)

# Register all tools
register_session_tools(app, get_db)
register_span_tools(app, get_db)
register_event_tools(app, get_db)
register_query_tools(app, get_db)
register_replay_tools(app, get_db)


if __name__ == "__main__":
    app.run(
        transport="http",
        host=settings.HOST,
        port=settings.PORT,
    )
