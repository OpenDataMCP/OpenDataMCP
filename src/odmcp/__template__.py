"""
Template for API Client Modules

This template provides a standardized structure for creating API client modules.
Each module should follow this pattern to ensure consistency across the codebase.

Module Structure:
1. Imports and Configuration
2. Global Constants
3. Registration Variables
4. Endpoint Sections (one per endpoint):
   - Pydantic Models (Input/Output)
   - Data Fetching Function
   - Handler Function
   - Tool Registration

Usage:
    Copy this template and replace the placeholders with actual implementation.
"""

# 1. Standard Imports Section
import logging
from typing import Any, List, Optional, Sequence

import httpx
import mcp.types as types
from pydantic import BaseModel, Field

# Initialize logging
log = logging.getLogger(__name__)

# 2. Constants Section
BASE_URL = "https://api.example.com/v1"

# 3. Registration Variables
RESOURCES: List[Any] = []  # Used for resource registration
TOOLS: List[types.Tool] = []  # For registering available tools
TOOLS_HANDLERS: dict[str, Any] = {}  # For mapping tools to handlers

###################
# [Endpoint Name]
###################


# 1. Input/Output Models
class EndpointParams(BaseModel):
    """Input parameters for the endpoint."""

    param1: str = Field(..., description="Description of param1")
    param2: Optional[int] = Field(None, description="Description of param2")


class EndpointResult(BaseModel):
    """Single result item from the endpoint."""

    field1: str = Field(..., description="Description of field1")
    field2: int = Field(..., description="Description of field2")


class EndpointResponse(BaseModel):
    """Complete response from the endpoint."""

    results: List[EndpointResult] = Field(..., description="List of results")


# 2. Data Fetching Function
def fetch_endpoint_data(params: EndpointParams) -> EndpointResponse:
    """
    Fetch data from the endpoint.

    Args:
        params: EndpointParams object containing all query parameters

    Returns:
        EndpointResponse object containing the results

    Raises:
        httpx.HTTPError: If the API request fails
    """
    endpoint = f"{BASE_URL}/endpoint"
    response = httpx.get(endpoint, params=params.model_dump(exclude_none=True))
    response.raise_for_status()
    return EndpointResponse(**response.json())


# 3. Handler Function
async def handle_endpoint(
    arguments: dict[str, Any] | None = None,
) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle the tool execution for this endpoint.

    Args:
        arguments: Dictionary of tool arguments

    Returns:
        Sequence of content objects

    Raises:
        Exception: If the handling fails
    """
    try:
        response = fetch_endpoint_data(EndpointParams(**(arguments or {})))
        return [types.TextContent(type="text", text=str(response))]
    except Exception as e:
        log.error(f"Error handling endpoint: {e}")
        raise


# 4. Tool Registration
TOOLS.append(
    types.Tool(
        name="endpoint-name",
        description="Description of what this endpoint does",
        inputSchema=EndpointParams.model_json_schema(),
    )
)
TOOLS_HANDLERS["endpoint-name"] = handle_endpoint

# Server initialization (if module is run directly)
if __name__ == "__main__":
    import anyio

    from odmcp.utils import run_server

    anyio.run(run_server, "service.name", TOOLS, TOOLS_HANDLERS)
