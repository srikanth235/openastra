from collections.abc import Callable
from typing import Literal

from mcp.server.fastmcp import FastMCP
from pydantic import Field

# Type for HTTP methods
HttpMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]

github_schema = {
    "app_id": "github",
    "id": "list_github_issues",
    "tool_schema": {
        "name": "ListGitHubIssues",
        "description": "Parameters for fetching GitHub issues via REST API",
        "parameters": {
            "type": "object",
            "properties": {
                "owner": {
                    "type": "string",
                    "description": "The account owner of the repository",
                },
                "repo": {
                    "type": "string",
                    "description": "The name of the repository",
                },
                "state": {
                    "type": "string",
                    "enum": ["open", "closed", "all"],
                    "default": "open",
                    "description": "Indicates the state of issues to return",
                },
                "assignee": {
                    "type": "string",
                    "description": "Filter issues by assignee. Can be 'none' for unassigned issues",
                },
                "creator": {
                    "type": "string",
                    "description": "Filter issues by creator",
                },
                "mentioned": {
                    "type": "string",
                    "description": "Filter issues by user mentioned in them",
                },
                "labels": {
                    "type": "string",
                    "description": "Comma-separated list of label names",
                },
                "sort": {
                    "type": "string",
                    "enum": ["created", "updated", "comments"],
                    "default": "created",
                    "description": "What to sort results by",
                },
                "direction": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "default": "desc",
                    "description": "The direction of the sort",
                },
                "since": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Only show issues updated at or after this time",
                },
                "per_page": {
                    "type": "integer",
                    "default": 30,
                    "description": "Number of results per page",
                },
                "page": {
                    "type": "integer",
                    "default": 1,
                    "description": "Page number of the results",
                },
            },
            "required": ["owner", "repo"],
        },
    },
    "tool_metadata": {
        "path": "/repos/{owner}/{repo}/issues",
        "method": "GET",
        "tags": ["issues", "list", "query"],
        "owner": {"type": "parameter", "in": "path"},
        "repo": {"type": "parameter", "in": "path"},
        "state": {"type": "parameter", "in": "query"},
        "assignee": {"type": "parameter", "in": "query"},
        "creator": {"type": "parameter", "in": "query"},
        "mentioned": {"type": "parameter", "in": "query"},
        "labels": {"type": "parameter", "in": "query"},
        "sort": {"type": "parameter", "in": "query"},
        "direction": {"type": "parameter", "in": "query"},
        "since": {"type": "parameter", "in": "query"},
        "per_page": {"type": "parameter", "in": "query"},
        "page": {"type": "parameter", "in": "query"},
    },
}


mcp = FastMCP("OpenAstra - MCP gateway for third party APIs")


@mcp.resource("echo://{message}")
def echo_resource(message: str) -> str:
    """Echo a message as a resource"""
    return f"Resource echo: {message}"


@mcp.tool()
def echo_tool(message: str) -> str:
    """Echo a message as a tool"""
    return f"Tool echo: {message}"


@mcp.tool()
def greet(
    name: str = Field(description="The name to greet"),
    title: str = Field(description="Optional title", default=""),
) -> str:
    """A greeting tool"""
    return f"Hello {title} {name}"


# Define example tools WITHOUT decorators - these will be loaded dynamically
def addition_tool(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b


# Register dynamic tools at startup
# This ensures tools are available when the MCP client connects
tools_to_load = [
    addition_tool,
    # schema_to_function(github_schema["tool_schema"], github_schema["tool_metadata"]),
]

for func in tools_to_load:
    decorated_func = mcp.tool()(func)
    print(f"Loaded tool at startup: {func.__name__}")


# For more advanced dynamic loading (if needed later)
def register_tool(func: Callable) -> Callable:
    """Register a function as a tool at runtime"""
    decorated_func = mcp.tool()(func)
    print(f"Dynamically registered tool: {func.__name__}")
    return decorated_func


# Add async function to delete tool after delay
def deregister_tool(tool_name: str) -> None:
    """Delete a tool after specified delay in seconds"""
    if tool_name in mcp._tool_manager._tools:
        del mcp._tool_manager._tools[tool_name]
        print(f"Deleted tool: {tool_name}")
