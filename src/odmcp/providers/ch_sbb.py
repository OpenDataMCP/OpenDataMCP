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
RESOURCES: List[Any] = []  # resources that will be registered by each endpoints
RESOURCES_HANDLERS: dict[
    str, Any
] = {}  # resources handlers that will be registered by each endpoints
TOOLS: List[types.Tool] = []  # tools that will be registered by each endpoints
TOOLS_HANDLERS: dict[
    str, Any
] = {}  # tools handlers that will be registered by each endpoints


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
    title: Optional[str] = Field(default=None, description="Title of the traffic info")
    link: Optional[str] = Field(default=None, description="URL to more details")
    description: Optional[str] = Field(
        default=None, description="Plain text description"
    )
    published: Optional[datetime] = Field(
        default=None, description="Publication timestamp"
    )
    author: Optional[str] = Field(
        default=None, description="Author of the traffic info"
    )
    validitybegin: Optional[datetime] = Field(
        default=None, description="Start time of the disruption"
    )
    validityend: Optional[datetime] = Field(
        default=None, description="End time of the disruption"
    )
    description_html: Optional[str] = Field(
        default=None, description="HTML formatted description"
    )


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
# Railway Line Information
###################


# 1. define models for the input / output
class RailwayLineParams(BaseModel):
    select: Optional[str] = Field(
        None,
        description="Fields to select in the response. Examples: 'linie,linienname' for basic info, 'bpk_anfang,bpk_ende' for station info",
    )
    where: Optional[str] = Field(
        None,
        description="Filter conditions. Examples: 'linie = 100', 'bpk_anfang LIKE \"*Zürich*\"'",
    )
    group_by: Optional[str] = Field(
        None,
        description="Group railway lines by specific fields. Example: 'bpk_anfang' to group by starting station",
    )
    order_by: Optional[str] = Field(
        None,
        description="Sort railway lines. Example: 'linie ASC' for line number order, 'km_ende DESC' for longest routes first",
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of railway line entries to return (1-100)",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of railway line entries to skip for pagination",
    )


class GeoPoint2D(BaseModel):
    lon: float = Field(description="Longitude coordinate")
    lat: float = Field(description="Latitude coordinate")


class LineGeometry(BaseModel):
    coordinates: List[List[float]] = Field(
        description="List of coordinate pairs [lon, lat]"
    )
    type: str = Field(description="Geometry type (usually 'LineString')")


class LineFeature(BaseModel):
    type: str = Field(description="Feature type")
    geometry: LineGeometry = Field(description="Line geometry information")
    properties: dict = Field(description="Additional properties")


class RailwayLineResult(BaseModel):
    linie: Optional[int] = Field(default=None, description="Line number")
    linienname: Optional[str] = Field(default=None, description="Line name/description")
    bpk_anfang: Optional[str] = Field(default=None, description="Starting station")
    bpk_ende: Optional[str] = Field(default=None, description="End station")
    km_anfang: Optional[float] = Field(default=None, description="Starting kilometer")
    km_ende: Optional[float] = Field(default=None, description="End kilometer")
    stationierung_anfang: Optional[int] = Field(
        default=None, description="Starting stationing"
    )
    stationierung_ende: Optional[int] = Field(
        default=None, description="End stationing"
    )
    tst: Optional[LineFeature] = Field(
        default=None, description="Geographic line feature"
    )
    geo_point_2d: Optional[GeoPoint2D] = Field(
        default=None, description="Center point of the line"
    )


class RailwayLineResponse(BaseModel):
    total_count: int = Field(description="Total number of results available")
    results: List[RailwayLineResult] = Field(description="List of railway line items")


# 2. define the function to fetch the data
def fetch_railway_lines(params: RailwayLineParams) -> RailwayLineResponse:
    """
    Fetch railway line information based on the provided parameters.

    Args:
        params: RailwayLineParams object containing all query parameters

    Returns:
        RailwayLineResponse object containing the results
    """
    endpoint = f"{BASE_URL}/catalog/datasets/linie/records"
    response = httpx.get(endpoint, params=params.model_dump(exclude_none=True))
    response.raise_for_status()
    return RailwayLineResponse(**response.json())


# 3. register the function to run when the tool is called
async def handle_railway_lines(
    arguments: dict[str, Any] | None = None,
) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    try:
        railway_lines_response = fetch_railway_lines(RailwayLineParams(**arguments))
        return [types.TextContent(type="text", text=str(railway_lines_response))]
    except Exception as e:
        log.error(f"Error fetching railway lines: {e}")
        raise


# 4. register the tool
TOOLS.append(
    types.Tool(
        name="railway-lines",
        description="Fetch railway line information",
        inputSchema=RailwayLineParams.model_json_schema(),
    )
)
TOOLS_HANDLERS["railway-lines"] = handle_railway_lines

###################
# Rolling Stock Information
###################


# 1. define models for the input / output
class RollingStockParams(BaseModel):
    select: Optional[str] = Field(
        None,
        description="Fields to select in the response. Examples: 'fahrzeug_typ,objekt' for basic info, 'vmax_betrieblich_zugelassen,lange_uber_puffer_lup' for technical details",
    )
    where: Optional[str] = Field(
        None,
        description="Filter conditions. Examples: 'fahrzeug_typ = \"X\"', 'vmax_betrieblich_zugelassen > 100'",
    )
    group_by: Optional[str] = Field(
        None,
        description="Group rolling stock by specific fields. Example: 'fahrzeug_typ' to group by vehicle type",
    )
    order_by: Optional[str] = Field(
        None,
        description="Sort rolling stock. Example: 'baudatum_fahrzeug ASC' for oldest first, 'vmax_betrieblich_zugelassen DESC' for fastest first",
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of rolling stock entries to return (1-100)",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of rolling stock entries to skip for pagination",
    )


class RollingStockResult(BaseModel):
    fahrzeug_art_struktur: Optional[str] = Field(
        default=None, description="Vehicle structure type"
    )
    fahrzeug_typ: Optional[str] = Field(default=None, description="Vehicle type")
    objekt: Optional[str] = Field(default=None, description="Vehicle identifier")
    baudatum_fahrzeug: Optional[str] = Field(default=None, description="Build date")
    eigengewicht_tara: Optional[float] = Field(default=None, description="Tare weight")
    lange_uber_puffer_lup: Optional[int] = Field(
        default=None, description="Length over buffers (mm)"
    )
    vmax_betrieblich_zugelassen: Optional[int] = Field(
        default=None, description="Maximum operational speed"
    )
    # Add other fields as needed, all as Optional since many can be null


class RollingStockResponse(BaseModel):
    total_count: int = Field(description="Total number of results available")
    results: List[RollingStockResult] = Field(description="List of rolling stock items")


# 2. define the function to fetch the data
def fetch_rolling_stock(params: RollingStockParams) -> RollingStockResponse:
    """
    Fetch rolling stock information based on the provided parameters.

    Args:
        params: RollingStockParams object containing all query parameters

    Returns:
        RollingStockResponse object containing the results
    """
    endpoint = f"{BASE_URL}/catalog/datasets/rollmaterial/records"
    response = httpx.get(endpoint, params=params.model_dump(exclude_none=True))
    response.raise_for_status()
    return RollingStockResponse(**response.json())


# 3. register the function to run when the tool is called
async def handle_rolling_stock(
    arguments: dict[str, Any] | None = None,
) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    try:
        rolling_stock_response = fetch_rolling_stock(RollingStockParams(**arguments))
        return [types.TextContent(type="text", text=str(rolling_stock_response))]
    except Exception as e:
        log.error(f"Error fetching rolling stock info: {e}")
        raise


# 4. register the tool
TOOLS.append(
    types.Tool(
        name="rolling-stock",
        description="Fetch rolling stock (vehicle) information",
        inputSchema=RollingStockParams.model_json_schema(),
    )
)
TOOLS_HANDLERS["rolling-stock"] = handle_rolling_stock


class StationUsersParams(BaseModel):
    select: Optional[str] = Field(
        None,
        description="Fields to select in the response. Examples: Bahnhof_Gare_Stazione for station name  ",
    )
    where: Optional[str] = Field(
        None,
        description="Filter conditions. Examples: 'linie = 100', 'bpk_anfang LIKE \"*Zürich*\"'",
    )
    group_by: Optional[str] = Field(
        None,
        description="Group railway lines by specific fields. Example: 'bpk_anfang' to group by starting station",
    )
    order_by: Optional[str] = Field(
        None,
        description="Sort stations. Example: 'Jahr' for line year order, 'Anzahl Bahnhofbenutzer DESC' for most used stations first",
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
        description="Number of  entries to skip for pagination",
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
    include_links: bool = Field(
        default=False, description="Include related links in response"
    )
    include_app_metas: bool = Field(
        default=False, description="Include application metadata"
    )


class StationUsersResult(BaseModel):
    bahnhof_gare_stazione: Optional[str] = Field(
        default=None, description="Station name"
    )
    jahr: Optional[int] = Field(default=None, description="Year of the traffic info")
    anzahl_bahnhofbenutzer: Optional[int] = Field(
        default=None, description="Users of the station"
    )


class StationUsersResponse(BaseModel):
    """Complete response from the endpoint."""

    total_count: int = Field(description="Total number of results available")
    results: List[StationUsersResult] = Field(description="List of traffic info items")


# 2. Data Fetching Function
def fetch_usage_data(params: StationUsersParams) -> StationUsersResponse:
    """
    Fetch data from the endpoint.

    Args:
        params: EndpointParams object containing all query parameters

    Returns:
        EndpointResponse object containing the results

    Raises:
        httpx.HTTPError: If the API request fails
    """
    endpoint = (
        f"{BASE_URL}/catalog/datasets/anzahl-sbb-bahnhofbenutzer/records?limit=100"
    )
    response = httpx.get(endpoint, params=params.model_dump(exclude_none=True))
    response.raise_for_status()
    return StationUsersResponse(**response.json())


# 3. Handler Function
async def handle_station_users(
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
        response = fetch_usage_data(StationUsersParams(**(arguments or {})))
        return [types.TextContent(type="text", text=str(response))]
    except Exception as e:
        log.error(f"Error handling endpoint: {e}")
        raise


# 4. Tool Registration
TOOLS.append(
    types.Tool(
        name="station-users",
        description="Description of what this endpoint does",
        inputSchema=StationUsersParams.model_json_schema(),
    )
)
TOOLS_HANDLERS["station-users"] = handle_station_users


class TargetActualComparedParams(BaseModel):
    select: Optional[str] = Field(
        None,
        description="Fields to select in the response. Examples: Bahnhof_Gare_Stazione for station name  ",
    )
    where: Optional[str] = Field(
        None,
        description="Filter conditions. Examples: 'linie = 100', 'bpk_anfang LIKE \"*Zürich*\"'",
    )
    group_by: Optional[str] = Field(
        None,
        description="Group railway lines by specific fields. Example: 'bpk_anfang' to group by starting station",
    )
    order_by: Optional[str] = Field(
        None,
        description="Sort stations. Example: 'Jahr' for line year order, 'Anzahl Bahnhofbenutzer DESC' for most used stations first",
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
        description="Number of  entries to skip for pagination",
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
    include_links: bool = Field(
        default=False, description="Include related links in response"
    )
    include_app_metas: bool = Field(
        default=False, description="Include application metadata"
    )


class TargetActualComparedResult(BaseModel):
    betriebstag: Optional[str] = Field(
        default=None, description="Operation day in YYYY-MM-DD format"
    )
    fahrt_bezeichner: Optional[str] = Field(
        default=None, description="Journey identifier"
    )
    betreiber_id: Optional[str] = Field(default=None, description="Operator ID")
    betreiber_abk: Optional[str] = Field(
        default=None, description="Operator abbreviation"
    )
    betreiber_name: Optional[str] = Field(
        default=None, description="Operator full name"
    )
    produkt_id: Optional[str] = Field(
        default=None, description="Product type, e.g., train (Zug)"
    )
    linien_id: Optional[int] = Field(default=None, description="Line ID")
    linien_text: Optional[str] = Field(default=None, description="Line text, e.g., S3")
    umlauf_id: Optional[str] = Field(
        default=None, description="Circle ID (if applicable)"
    )
    verkehrsmittel_text: Optional[str] = Field(
        default=None, description="Mode of transport, e.g., train type"
    )
    zusatzfahrt_tf: Optional[bool] = Field(
        default=None, description="Indicates if it's an additional trip"
    )
    faellt_aus_tf: Optional[bool] = Field(
        default=None, description="Indicates if the trip is canceled"
    )
    bpuic: Optional[int] = Field(default=None, description="Station BPUIC code")
    haltestellen_name: Optional[str] = Field(default=None, description="Station name")
    ankunftszeit: Optional[str] = Field(
        default=None, description="Scheduled arrival time"
    )
    an_prognose: Optional[str] = Field(
        default=None, description="Predicted arrival time"
    )
    an_prognose_status: Optional[str] = Field(
        default=None, description="Status of the arrival prediction"
    )
    abfahrtszeit: Optional[str] = Field(
        default=None, description="Scheduled departure time"
    )
    ab_prognose: Optional[str] = Field(
        default=None, description="Predicted departure time"
    )
    ab_prognose_status: Optional[str] = Field(
        default=None, description="Status of the departure prediction"
    )
    durchfahrt_tf: Optional[bool] = Field(
        default=None, description="Indicates if it's a pass-through without stop"
    )
    ankunftsverspatung: Optional[bool] = Field(
        default=None, description="Indicates if there is an arrival delay"
    )
    abfahrtsverspatung: Optional[bool] = Field(
        default=None, description="Indicates if there is a departure delay"
    )
    geopos: Optional[GeoPoint2D] = Field(
        default=None,
        description="Geographical position as a dictionary with 'lon' and 'lat'",
    )
    lod: Optional[str] = Field(default=None, description="Linked Open Data (LOD) URL")


class TargetActualComparedResponse(BaseModel):
    """Complete response from the endpoint."""

    total_count: int = Field(description="Total number of results available")
    results: List[TargetActualComparedResult] = Field(
        ..., description="List of results"
    )


# 2. Data Fetching Function
def fetch_target_actual_compared(
    params: TargetActualComparedParams,
) -> TargetActualComparedResponse:
    """
    Fetch data from the endpoint.

    Args:
        params: EndpointParams object containing all query parameters

    Returns:
        EndpointResponse object containing the results

    Raises:
        httpx.HTTPError: If the API request fails
    """
    endpoint = f"{BASE_URL}/catalog/datasets/ist-daten-sbb/records?limit=100"
    response = httpx.get(endpoint, params=params.model_dump(exclude_none=True))
    response.raise_for_status()
    return TargetActualComparedResponse(**response.json())


# 3. Handler Function
async def handle_target_actual_compared(
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
        response = fetch_target_actual_compared(
            TargetActualComparedParams(**(arguments or {}))
        )
        return [types.TextContent(type="text", text=str(response))]
    except Exception as e:
        log.error(f"Error handling endpoint: {e}")
        raise


# 4. Tool Registration
TOOLS.append(
    types.Tool(
        name="target-actual-compared",
        description="Description of what this endpoint does",
        inputSchema=TargetActualComparedParams.model_json_schema(),
    )
)
TOOLS_HANDLERS["target-actual-compared"] = handle_target_actual_compared


class StationFurnitureParams(BaseModel):
    select: Optional[str] = Field(
        None,
        description="Fields to select in the response. Examples: 'bezeichnung', 'bezeichnung_offiziell'",
    )
    where: Optional[str] = Field(
        None,
        description="Filter conditions. Examples: 'we = \"50001\"', 'bpuic = 8502113'",
    )
    group_by: Optional[str] = Field(
        None,
        description="Group results by specific fields. Example: 'bezeichnung' to group by the object name",
    )
    order_by: Optional[str] = Field(
        None,
        description="Sort stations. Example: 'flame2 DESC' for highest attribute value first",
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of results to return (1-100)",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of entries to skip for pagination",
    )
    refine: Optional[str] = Field(
        None,
        description="Refine by specific fields. Example: 'lod:http://lod.opentransportdata.swiss/didok/8502113'",
    )
    exclude: Optional[str] = Field(
        None,
        description="Exclude specific fields from response. Example: 'geopos' to exclude location data",
    )
    lang: Optional[str] = Field(
        None,
        description="Language code for responses (de, fr, it, en). Affects returned content language",
    )
    include_links: bool = Field(
        default=False, description="Include related links in response"
    )
    include_app_metas: bool = Field(
        default=False, description="Include application metadata"
    )


class StationFurnitureResult(BaseModel):
    we: Optional[str] = Field(
        default=None, description="Unique identifier, e.g., the station code"
    )
    didok: Optional[int] = Field(
        default=None, description="DIDOK number (Swiss transport identifier)"
    )
    bezeichnung: Optional[str] = Field(
        default=None, description="Name or designation of the object"
    )
    flame2: Optional[float] = Field(
        default=None, description="Measurement or attribute related to the object"
    )
    einheit: Optional[str] = Field(
        default=None, description="Unit of measurement for the attribute"
    )
    bezeichnung_offiziell: Optional[str] = Field(
        default=None, description="Official designation of the location"
    )
    lod: Optional[str] = Field(
        default=None, description="Linked Open Data reference URL"
    )
    geopos: Optional[GeoPoint2D] = Field(
        default=None,
        description="Geoposition as a dictionary containing longitude and latitude",
    )
    tu_nummer: Optional[int] = Field(default=None, description="Transport unit number")
    bpuic: Optional[int] = Field(
        default=None, description="BPUIC code for transport infrastructure"
    )


class StationFurnitureResponse(BaseModel):
    """Complete response from the endpoint."""

    total_count: int = Field(description="Total number of results available")
    results: List[StationFurnitureResult] = Field(..., description="List of results")


# 2. Data Fetching Function
def fetch_station_furnitures(
    params: StationFurnitureParams,
) -> StationFurnitureResponse:
    """
    Fetch data from the endpoint.

    Args:
        params: EndpointParams object containing all query parameters

    Returns:
        EndpointResponse object containing the results

    Raises:
        httpx.HTTPError: If the API request fails
    """

    endpoint = f"{BASE_URL}/catalog/datasets/mobiliar-im-bahnhof/records?limit=100"
    response = httpx.get(endpoint, params=params.model_dump(exclude_none=True))
    response.raise_for_status()
    return StationFurnitureResponse(**response.json())


# 3. Handler Function
async def handle_station_furnitures(
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
        response = fetch_station_furnitures(StationFurnitureParams(**(arguments or {})))
        return [types.TextContent(type="text", text=str(response))]
    except Exception as e:
        log.error(f"Error handling endpoint: {e}")
        raise


# 4. Tool Registration
TOOLS.append(
    types.Tool(
        name="station-furniture",
        description="Description of what this endpoint does",
        inputSchema=StationFurnitureParams.model_json_schema(),
    )
)
TOOLS_HANDLERS["station-furniture"] = handle_station_furnitures


class StationServiceParams(BaseModel):
    select: Optional[str] = Field(
        None,
        description="Fields to select in the response. Examples: 'stationsbezeichnung', 'servicename'",
    )
    where: Optional[str] = Field(
        None,
        description="Filter conditions. Examples: 'dst_nr = 10', 'wochentag = \"01-01-04\"'",
    )
    group_by: Optional[str] = Field(
        None,
        description="Group results by specific fields. Example: 'feiertag' to group by holidays",
    )
    order_by: Optional[str] = Field(
        None,
        description="Sort results. Example: 'von1 ASC' for earliest service time first",
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of results to return (1-100)",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of entries to skip for pagination",
    )
    refine: Optional[str] = Field(
        None,
        description="Refine by specific fields. Example: 'unternehmung:SBB' to show only SBB services",
    )
    exclude: Optional[str] = Field(
        None,
        description="Exclude specific fields from response. Example: 'geopos' to exclude location data",
    )
    lang: Optional[str] = Field(
        None,
        description="Language code for responses (de, fr, it, en). Affects returned content language",
    )
    include_links: bool = Field(
        default=False, description="Include related links in response"
    )
    include_app_metas: bool = Field(
        default=False, description="Include application metadata"
    )


class StationServiceResult(BaseModel):
    dst_nr: Optional[int] = Field(default=None, description="Station service number")
    stationsbezeichnung: Optional[str] = Field(default=None, description="Station name")
    datum: Optional[str] = Field(default=None, description="Date of the service")
    feiertag: Optional[str] = Field(default=None, description="Holiday name")
    wochentag: Optional[str] = Field(
        default=None, description="Day of the week in 'DD-MM-YY' format"
    )
    national: Optional[int] = Field(
        default=None, description="Indicates if the service is national (1 = yes)"
    )
    servicetyp: Optional[int] = Field(
        default=None, description="Service type identifier"
    )
    servicename: Optional[str] = Field(default=None, description="Name of the service")
    closed: Optional[str] = Field(
        default=None, description="Indicates if the service is closed (null if open)"
    )
    von1: Optional[str] = Field(
        default=None, description="Service start time for the first period"
    )
    bis1: Optional[str] = Field(
        default=None, description="Service end time for the first period"
    )
    von2: Optional[str] = Field(
        default=None, description="Service start time for the second period"
    )
    bis2: Optional[str] = Field(
        default=None, description="Service end time for the second period"
    )
    von3: Optional[str] = Field(
        default=None, description="Service start time for the third period"
    )
    bis3: Optional[str] = Field(
        default=None, description="Service end time for the third period"
    )
    unternehmung: Optional[str] = Field(
        default=None, description="Name of the company providing the service"
    )
    bpuic: Optional[int] = Field(
        default=None, description="BPUIC code for transport infrastructure"
    )
    bezeichnung_offiziell: Optional[str] = Field(
        default=None, description="Official designation of the station"
    )
    abkuerzung: Optional[str] = Field(
        default=None, description="Abbreviation for the station"
    )
    lod: Optional[str] = Field(
        default=None, description="Linked Open Data reference URL"
    )
    geopos: Optional[GeoPoint2D] = Field(
        default=None,
        description="Geoposition as a dictionary containing longitude and latitude",
    )
    tu_nummer: Optional[int] = Field(default=None, description="Transport unit number")
    meteo: Optional[str] = Field(
        default=None, description="URL to the weather information for the station"
    )
    plz: Optional[str] = Field(default=None, description="Postal code of the station")


class StationServiceResponse(BaseModel):
    """Complete response from the endpoint."""

    total_count: int = Field(description="Total number of results available")

    results: List[StationServiceResult] = Field(..., description="List of results")


# 2. Data Fetching Function
def fetch_station_services(params: StationServiceParams) -> StationServiceResponse:
    """
    Fetch data from the endpoint.

    Args:
        params: EndpointParams object containing all query parameters

    Returns:
        EndpointResponse object containing the results

    Raises:
        httpx.HTTPError: If the API request fails
    """
    endpoint = (
        f"{BASE_URL}/catalog/datasets/haltestelle-offnungszeiten/records?limit=100"
    )
    response = httpx.get(endpoint, params=params.model_dump(exclude_none=True))
    response.raise_for_status()
    return StationServiceResponse(**response.json())


# 3. Handler Function
async def handle_station_services(
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
        response = fetch_station_services(StationServiceParams(**(arguments or {})))
        return [types.TextContent(type="text", text=str(response))]
    except Exception as e:
        log.error(f"Error handling endpoint: {e}")
        raise


# 4. Tool Registration
TOOLS.append(
    types.Tool(
        name="station-services",
        description="Description of what this endpoint does",
        inputSchema=StationServiceParams.model_json_schema(),
    )
)
TOOLS_HANDLERS["station-services"] = handle_station_services


class StoresParams(BaseModel):
    select: Optional[str] = Field(
        None,
        description="Fields to select in the response. Examples: 'station_uic', 'name_de', 'openinghours'",
    )
    where: Optional[str] = Field(
        None,
        description="Filter conditions. Examples: 'category = \"sbb_services\"', 'station_uic = 8509000'",
    )
    group_by: Optional[str] = Field(
        None,
        description="Group results by specific fields. Example: 'holiday' to group by holidays",
    )
    order_by: Optional[str] = Field(
        None,
        description="Sort results. Example: 'valid_from ASC' for earliest opening times first",
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of results to return (1-100)",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of entries to skip for pagination",
    )
    refine: Optional[str] = Field(
        None,
        description="Refine by specific fields. Example: 'language_station:DE' to show only German stations",
    )
    exclude: Optional[str] = Field(
        None,
        description="Exclude specific fields from response. Example: 'icon_svg' to exclude service icons",
    )
    lang: Optional[str] = Field(
        None,
        description="Language code for responses (de, fr, it, en). Affects returned content language",
    )
    include_links: bool = Field(
        default=False, description="Include related links in response"
    )
    include_app_metas: bool = Field(
        default=False, description="Include application metadata"
    )

    """Cant get this working even tho its mapping what it returns....

    Returns:
       
    """


class InfoText(BaseModel):
    de: Optional[str] = Field(description="Information text in German")
    en: Optional[str] = Field(description="Information text in English")
    fr: Optional[str] = Field(description="Information text in French")
    it: Optional[str] = Field(description="Information text in Italian")


class ContactItem(BaseModel):
    type: str = Field(description="Type of contact information, e.g., 'phone'")
    value: str = Field(
        description="The value of the contact, e.g., phone number or email address"
    )
    access: str = Field(description="Access level for the contact, e.g., 'public'")
    lang: Optional[str] = Field(
        default=None, description="Language of the contact information, if applicable"
    )
    info_text: Optional[InfoText] = Field(
        default=None, description="Localized information texts for the contact"
    )


class OpeningHours(BaseModel):
    day_from: int = Field(description="Starting day of the week (0=Monday, 6=Sunday)")
    day_to: int = Field(description="Ending day of the week (0=Monday, 6=Sunday)")
    time_from: str = Field(description="Opening time in HH:MM:SS format")
    time_to: str = Field(description="Closing time in HH:MM:SS format")


class Holiday(BaseModel):
    date: str = Field(description="Date of the holiday in YYYY-MM-DD format")
    name_de: Optional[str] = Field(description="Holiday name in German")
    name_en: Optional[str] = Field(description="Holiday name in English")
    name_fr: Optional[str] = Field(description="Holiday name in French")
    name_it: Optional[str] = Field(description="Holiday name in Italian")
    holiday_type: Optional[str] = Field(
        description="Type of holiday (e.g., national, regional)"
    )


class ScheduleItem(BaseModel):
    valid_from: str = Field(
        description="Date from which the schedule is valid in YYYY-MM-DD format"
    )
    valid_until: Optional[str] = Field(
        description="Date until which the schedule is valid in YYYY-MM-DD format"
    )
    openinghours: List[OpeningHours] = Field(
        description="List of opening hours for the schedule"
    )
    holiday: Optional[Any] = Field(description="Holiday information, if applicable")


class Schedule(BaseModel):
    schedule: dict[Any, List[ScheduleItem]]


##cant get the mapping to work
class StoresResult(BaseModel):
    station_uic: Optional[int] = Field(default=None, description="Station UIC code")
    category: Optional[str] = Field(
        default=None, description="Main category of the service"
    )
    subcategory: Optional[str] = Field(
        default=None, description="Subcategory of the service"
    )
    name_de: Optional[str] = Field(default=None, description="Service name in German")
    name_fr: Optional[str] = Field(default=None, description="Service name in French")
    name_it: Optional[str] = Field(default=None, description="Service name in Italian")
    name_en: Optional[str] = Field(default=None, description="Service name in English")
    icon_svg: Optional[str] = Field(default=None, description="URL to the service icon")
    contacts: Optional[Any] = Field(
        default=None,
        description="Contact information, including type, value, and info text in multiple languages",
    )
    openinghours: Optional[Any] = Field(
        default=None,
        description="Opening hours for the service with details on validity and holidays",
    )
    geo: Optional[GeoPoint2D] = Field(
        default=None,
        description="Geoposition as a dictionary containing longitude and latitude",
    )
    location_details_de: Optional[str] = Field(
        default=None, description="Location details in German"
    )
    location_details_fr: Optional[str] = Field(
        default=None, description="Location details in French"
    )
    location_details_it: Optional[str] = Field(
        default=None, description="Location details in Italian"
    )
    location_details_en: Optional[str] = Field(
        default=None, description="Location details in English"
    )

    floor: Optional[Any] = Field(
        default=None,
        description="Floor details including level and names in multiple languages",
    )
    url_identifier: Optional[str] = Field(
        default=None, description="Unique URL identifier for the service"
    )
    url_alias: Optional[str] = Field(
        default=None, description="Alias for the service URL"
    )
    businee_name: Optional[str] = Field(
        default=None, description="Business name associated with the service"
    )
    meteo: Optional[str] = Field(
        default=None, description="URL to the weather information for the station"
    )
    bezeichnung_offiziell: Optional[str] = Field(
        default=None, description="Official designation of the station"
    )
    display_name: Optional[str] = Field(
        default=None, description="Display name of the service"
    )


class StoresResponse(BaseModel):
    """Complete response from the endpoint."""

    total_count: int = Field(description="Total number of results available")
    results: List[StoresResult] = Field(..., description="List of results")


# 2. Data Fetching Function
def fetch_stores_data(params: StoresParams) -> StoresResponse:
    """
    Fetch data from the endpoint.

    Args:
        params: EndpointParams object containing all query parameters

    Returns:
        EndpointResponse object containing the results

    Raises:
        httpx.HTTPError: If the API request fails
    """
    endpoint = f"{BASE_URL}/catalog/datasets/offnungszeiten-shops/records?limit=100"
    response = httpx.get(endpoint, params=params.model_dump(exclude_none=True))
    response.raise_for_status()
    return StoresResponse(**response.json())


# 3. Handler Function
async def hande_stores_data(
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
        response = fetch_stores_data(StoresParams(**(arguments or {})))
        return [types.TextContent(type="text", text=str(response))]
    except Exception as e:
        log.error(f"Error handling endpoint: {e}")
        raise


# 4. Tool Registration
TOOLS.append(
    types.Tool(
        name="station-stores",
        description="Description of what this endpoint does",
        inputSchema=StoresParams.model_json_schema(),
    )
)
TOOLS_HANDLERS["station-stores"] = hande_stores_data
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
    # anyio.run(main)

    # test the endpoints
    # print(
    #    "Rail Traffic Info:",
    #    fetch_rail_traffic_info(TrafficInfoParams(select="title,description", limit=1)),
    # )
    # print(
    #     "Railway Lines:",
    #     fetch_railway_lines(RailwayLineParams(select="tst", limit=1)),
    # )
    # print(
    #    "Rolling Stock:",
    #    fetch_rolling_stock(RollingStockParams(select="fahrzeug_typ,objekt", limit=1)),
    # )
    # print(
    #    "Usage Info",
    #    fetch_usage_data(StationUsersParams(select="", limit=1)),
    # )
    # print(
    #    "Target Actual Compared:",
    #    fetch_target_actual_compared(TargetActualComparedParams(select="", limit=1)),
    # )
    #
    # print(
    #    "Station Info:",
    #    fetch_station_furnitures(StationFurnitureParams(select="", limit=1)),
    # )
    # print(
    #    "station services",
    #    fetch_station_services(StationServiceParams(select="", limit=1)),
    # )
    print(
        "getstore data ",
        fetch_stores_data(StoresParams(select="openinghours", limit=1)),
    )
