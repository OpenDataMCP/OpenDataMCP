"""
Swiss Federal Railways (SBB) Data API Client

This module provides interfaces to access various endpoints of the SBB Data API (data.sbb.ch).
It includes tools and handlers for retrieving rail traffic information and other railway-related
data through the SBB's public API endpoints.

Features:
- Rail traffic information retrieval
- Configurable query parameters
- Response parsing and type validation using Pydantic models

Usage:
    The module can be run directly to start a server handling API requests,
    or its components can be imported and used individually.
"""

import logging
from datetime import datetime
from typing import Any, List, Optional, Sequence

import httpx
import mcp.types as types
from mcp.server import stdio_server
from pydantic import BaseModel, Field

log = logging.getLogger(__name__)

BASE_URL = "https://data.sbb.ch/api/explore/v2.1"

# Registration Variables
RESOURCES = []  # resources that will be registered by each endpoints
RESOURCES_HANDLERS = {}  # resources handlers that will be registered by each endpoints
TOOLS = []  # tools that will be registered by each endpoints
TOOLS_HANDLERS = {}  # tools handlers that will be registered by each endpoints


###################
# Rail Traffic Information
###################


# 1. define models for the input / output
class TrafficInfoParams(BaseModel):
    select: Optional[str] = Field(
        None,
        description="Fields to select in the response. Examples: 'title,description' for basic info, 'title,validitybegin,validityend' for timing info",
    )
    where: Optional[str] = Field(
        None,
        description="Filter conditions for traffic info. Examples: 'validitybegin >= NOW()', 'description LIKE \"*Zürich*\"'",
    )
    group_by: Optional[str] = Field(
        None,
        description="Group traffic info by specific fields. Example: 'author' to group by the author of the traffic info",
    )
    order_by: Optional[str] = Field(
        None,
        description="Sort traffic info. Example: 'validitybegin ASC' for chronological order, 'published DESC' for newest first",
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of traffic info entries to return (1-100)",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of traffic info entries to skip for pagination",
    )
    refine: Optional[str] = Field(
        None,
        description="Refine by specific facets. Example: 'author:SBB' to show only SBB notifications",
    )
    exclude: Optional[str] = Field(
        None,
        description="Exclude specific fields from response. Example: 'description_html' to exclude HTML formatting",
    )
    lang: Optional[str] = Field(
        None,
        description="Language code for responses (de, fr, it, en). Affects message content language",
    )
    timezone: str = Field(
        default="UTC",
        description="Timezone for validity and publication times. Example: 'Europe/Zurich' for local Swiss time",
    )
    include_links: bool = Field(
        default=False, description="Include related links in response"
    )
    include_app_metas: bool = Field(
        default=False, description="Include application metadata"
    )


class TrafficInfoResult(BaseModel):
    title: str = Field(description="Title of the traffic info")
    link: str = Field(description="URL to more details")
    description: str = Field(description="Plain text description")
    published: datetime = Field(description="Publication timestamp")
    author: str = Field(description="Author of the traffic info")
    validitybegin: datetime = Field(description="Start time of the disruption")
    validityend: datetime = Field(description="End time of the disruption")
    description_html: str = Field(description="HTML formatted description")


class TrafficInfoResponse(BaseModel):
    total_count: int = Field(description="Total number of results available")
    results: List[TrafficInfoResult] = Field(description="List of traffic info items")


# 2. define the function to fetch the data
def fetch_rail_traffic_info(params: TrafficInfoParams) -> TrafficInfoResponse:
    """
    Fetch rail traffic information based on the provided parameters.

    Args:
        params: TrafficInfoParams object containing all query parameters

    Returns:
        TrafficInfoResponse object containing the results
    """
    # Implementation here
    ...
    endpoint = f"{BASE_URL}/catalog/datasets/rail-traffic-information/records"
    response = httpx.get(endpoint, params=params.model_dump(exclude_none=True))

    response.raise_for_status()

    return TrafficInfoResponse(**response.json())


# 3. register the function to run when the tool is called
async def handle_rail_traffic_info(
    arguments: dict[str, Any] | None = None,
) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    try:
        traffic_info_response = fetch_rail_traffic_info(TrafficInfoParams(**arguments))
        return [types.TextContent(type="text", text=str(traffic_info_response))]
    except Exception as e:
        log.error(f"Error fetching rail traffic info: {e}")
        raise


# 4. register the tool
TOOLS.append(
    types.Tool(
        name="rail-traffic-info",
        description="Fetch rail traffic information",
        inputSchema=TrafficInfoParams.model_json_schema(),
    )
)
TOOLS_HANDLERS["rail-traffic-info"] = handle_rail_traffic_info

###################
# Other Endpoint Name
###################
...


async def main():
    from odmcp.utils import create_mcp_server

    # create the server
    server = create_mcp_server(
        "data.sbb.ch", RESOURCES, RESOURCES_HANDLERS, TOOLS, TOOLS_HANDLERS
    )

    # run the server
    async with stdio_server() as streams:
        await server.run(streams[0], streams[1], server.create_initialization_options())


if __name__ == "__main__":
    import anyio

    anyio.run(main)
