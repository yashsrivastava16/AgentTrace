"""
FastMCP application entry point.
Initializes the MCP server, registers all tools, and starts the server.
"""
from fastmcp import FastMCP
from fastmcp.server.middleware import MiddlewareContext
from mcp_tracer.core.config import settings
from mcp_tracer.core.security import verify_token
from mcp_tracer.core.logging import logger
from mcp_tracer.core.lifespan import lifespan 
from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware
from fastmcp.server.dependencies import get_http_headers
from mcp_tracer.tools import (
    register_session_tools,
    register_span_tools,
    register_event_tools,
    register_query_tools,
    register_replay_tools,
)

# Initialize FastMCP app
app = FastMCP(settings.APP_NAME, lifespan=lifespan)

class JWTAuthMiddleware(Middleware):
    # Tools that don't need a session scope — agent token is enough
    ENV_TOOLS = {
        'development': {
            "create_session", "query_cross_session", "start_span", 
            "end_span", "log_event", "replay_session", 
            "complete_session", "fail_session"
        },
        'default': {"create_session", "query_cross_session"}
    }

    SESSION_FREE_TOOLS = ENV_TOOLS.get(settings.APP_ENV, ENV_TOOLS['default'])
    async def on_call_tool(self, context, call_next):
        # FastMCP passes request metadata via `context.request_context` in some versions,
        # but not all integrations populate it. Fall back to empty metadata.
        headers = get_http_headers(include_all=True)
        tool_name = context.message.name

        if tool_name in self.SESSION_FREE_TOOLS:
            return await call_next(context)
        else:
            auth_header = headers.get("authorization") or headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise ToolError("Unauthorized: missing or invalid Authorization header")
            else:
                token = auth_header.removeprefix("Bearer ").strip()
                payload = verify_token(token)
                token_type = payload.get("token_type", "agent")


        # Session-free tools — agent token is sufficient, no scope check
        if tool_name in self.SESSION_FREE_TOOLS:
            logger.info(f"Authenticated | subject='{payload.get('sub')}' | tool='{tool_name}' | type=agent")
            return await call_next(context)

        # All other tools — require session token scoped to the right session
        if token_type != "session":
            raise ToolError(
                f"Tool '{tool_name}' requires a session-scoped token. "
                f"Call create_session first to get a session_id, "
                f"then generate a session token."
            )

        token_session = payload.get("session_id")
        tool_input = context.arguments or {}

        if "session_id" in tool_input and token_session != tool_input["session_id"]:
            raise ToolError(
                f"Unauthorized: token scoped to '{token_session}' "
                f"but request targets '{tool_input['session_id']}'"
            )

        logger.info(
            f"Authenticated | subject='{payload.get('sub')}' | "
            f"tool='{tool_name}' | session='{token_session}'"
        )

        return await call_next(context)


app.add_middleware(JWTAuthMiddleware())

# Register all tools
register_session_tools(app)
register_span_tools(app)
register_event_tools(app)
register_query_tools(app)
register_replay_tools(app)


if __name__ == "__main__":
    app.run(
        transport="http",
        host=settings.HOST,
        port=settings.PORT,
    )
