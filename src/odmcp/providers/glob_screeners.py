"""
Template for MCP server definitions.

This template provides a standardized structure for creating MCP server modules.
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
import yfinance as yf
import mcp.types as types
from pydantic import BaseModel, Field

# Initialize logging
log = logging.getLogger(__name__)

# 2. Global Constants
screener = yf.Screener()
# 3. Registration Variables
RESOURCES: List[Any] = []  # resources that will be registered by each endpoints
RESOURCES_HANDLERS: dict[
    str, Any
] = {}  # resources handlers that will be registered by each endpoints
TOOLS: List[types.Tool] = []  # tools that will be registered by each endpoints
TOOLS_HANDLERS: dict[
    str, Any
] = {}  # tools handlers that will be registered by each endpoints

###################
# [Endpoint Name]
###################


# 1. Input/Output Models
class FincanceScreenerParams(BaseModel):
    """Input parameters for the endpoint."""

    screenerOptions: str = Field(
        default="day_gainers",
        description=(
            "Screener options from the following list: "
            "aggressive_small_caps, day_gainers, day_losers, growth_technology_stocks, "
            "most_actives, most_shorted_stocks, small_cap_gainers, "
            "undervalued_growth_stocks, undervalued_large_caps, conservative_foreign_funds, "
            "high_yield_bond, portfolio_anchors, solid_large_growth_funds, "
            "solid_midcap_growth_funds, top_mutual_funds"
        ),
    )


class FincanceScreenerResult(BaseModel):
    """Single result item from the endpoint."""

    language: Optional[str] = Field(None, description="Language setting of the result.")
    region: Optional[str] = Field(None, description="Region setting of the result.")
    quoteType: Optional[str] = Field(
        None, description="Type of the quote (e.g., EQUITY)."
    )
    typeDisp: Optional[str] = Field(None, description="Display type of the quote.")
    quoteSourceName: Optional[str] = Field(
        None, description="Source name for the quote."
    )
    triggerable: Optional[bool] = Field(
        None, description="Whether the quote is triggerable."
    )
    customPriceAlertConfidence: Optional[str] = Field(
        None, description="Confidence level of the price alert."
    )
    currency: Optional[str] = Field(None, description="Currency of the market data.")
    shortName: Optional[str] = Field(None, description="Short name of the company.")
    regularMarketDayRange: Optional[str] = Field(
        None, description="Range of market day prices."
    )
    regularMarketDayLow: Optional[float] = Field(
        None, description="Lowest price of the day."
    )
    regularMarketVolume: Optional[int] = Field(
        None, description="Trading volume during regular market hours."
    )
    regularMarketPreviousClose: Optional[float] = Field(
        None, description="Closing price of the previous day."
    )
    bid: Optional[float] = Field(None, description="Current bid price.")
    ask: Optional[float] = Field(None, description="Current ask price.")
    bidSize: Optional[int] = Field(None, description="Size of the bid.")
    askSize: Optional[int] = Field(None, description="Size of the ask.")
    market: Optional[str] = Field(None, description="Market identifier.")
    messageBoardId: Optional[str] = Field(None, description="Message board ID.")
    fullExchangeName: Optional[str] = Field(
        None, description="Full name of the exchange."
    )
    longName: Optional[str] = Field(None, description="Full name of the company.")
    financialCurrency: Optional[str] = Field(
        None, description="Financial currency of the company."
    )
    regularMarketOpen: Optional[float] = Field(
        None, description="Opening price of the market."
    )
    averageDailyVolume3Month: Optional[int] = Field(
        None, description="Average daily trading volume over three months."
    )
    averageDailyVolume10Day: Optional[int] = Field(
        None, description="Average daily trading volume over ten days."
    )
    fiftyTwoWeekLowChange: Optional[float] = Field(
        None, description="Change from the 52-week low price."
    )
    fiftyTwoWeekLowChangePercent: Optional[float] = Field(
        None, description="Percentage change from the 52-week low price."
    )
    fiftyTwoWeekRange: Optional[str] = Field(
        None, description="Range of 52-week prices."
    )
    fiftyTwoWeekHighChange: Optional[float] = Field(
        None, description="Change from the 52-week high price."
    )
    fiftyTwoWeekHighChangePercent: Optional[float] = Field(
        None, description="Percentage change from the 52-week high price."
    )
    fiftyTwoWeekChangePercent: Optional[float] = Field(
        None, description="Percentage change over the 52-week range."
    )
    earningsTimestamp: Optional[int] = Field(None, description="Earnings timestamp.")
    earningsTimestampStart: Optional[int] = Field(
        None, description="Start of the earnings timestamp range."
    )
    earningsTimestampEnd: Optional[int] = Field(
        None, description="End of the earnings timestamp range."
    )
    earningsCallTimestampStart: Optional[int] = Field(
        None, description="Start of the earnings call timestamp."
    )
    earningsCallTimestampEnd: Optional[int] = Field(
        None, description="End of the earnings call timestamp."
    )
    isEarningsDateEstimate: Optional[bool] = Field(
        None, description="Indicates if the earnings date is an estimate."
    )
    trailingAnnualDividendRate: Optional[float] = Field(
        None, description="Trailing annual dividend rate."
    )
    trailingAnnualDividendYield: Optional[float] = Field(
        None, description="Trailing annual dividend yield."
    )
    marketState: Optional[str] = Field(None, description="Current state of the market.")
    epsTrailingTwelveMonths: Optional[float] = Field(
        None, description="Earnings per share over the trailing twelve months."
    )
    epsForward: Optional[float] = Field(
        None, description="Forward-looking earnings per share."
    )
    epsCurrentYear: Optional[float] = Field(
        None, description="Earnings per share for the current year."
    )
    priceEpsCurrentYear: Optional[float] = Field(
        None, description="Price to earnings ratio for the current year."
    )
    sharesOutstanding: Optional[int] = Field(
        None, description="Number of outstanding shares."
    )
    bookValue: Optional[float] = Field(None, description="Book value per share.")
    fiftyDayAverage: Optional[float] = Field(None, description="50-day average price.")
    fiftyDayAverageChange: Optional[float] = Field(
        None, description="Change from the 50-day average price."
    )
    fiftyDayAverageChangePercent: Optional[float] = Field(
        None, description="Percentage change from the 50-day average price."
    )
    twoHundredDayAverage: Optional[float] = Field(
        None, description="200-day average price."
    )
    twoHundredDayAverageChange: Optional[float] = Field(
        None, description="Change from the 200-day average price."
    )
    twoHundredDayAverageChangePercent: Optional[float] = Field(
        None, description="Percentage change from the 200-day average price."
    )
    marketCap: Optional[int] = Field(None, description="Market capitalization.")
    forwardPE: Optional[float] = Field(
        None, description="Forward price to earnings ratio."
    )
    priceToBook: Optional[float] = Field(None, description="Price to book ratio.")
    sourceInterval: Optional[int] = Field(
        None, description="Source interval in seconds."
    )
    exchangeDataDelayedBy: Optional[int] = Field(
        None, description="Delay time for exchange data in seconds."
    )
    exchangeTimezoneName: Optional[str] = Field(
        None, description="Timezone name of the exchange."
    )
    exchangeTimezoneShortName: Optional[str] = Field(
        None, description="Short timezone name of the exchange."
    )
    gmtOffSetMilliseconds: Optional[int] = Field(
        None, description="GMT offset in milliseconds."
    )
    esgPopulated: Optional[bool] = Field(
        None, description="Indicates if ESG data is populated."
    )
    tradeable: Optional[bool] = Field(
        None, description="Indicates if the item is tradeable."
    )
    cryptoTradeable: Optional[bool] = Field(
        None, description="Indicates if the item is tradeable as cryptocurrency."
    )
    hasPrePostMarketData: Optional[bool] = Field(
        None, description="Indicates if pre and post-market data is available."
    )
    firstTradeDateMilliseconds: Optional[int] = Field(
        None, description="Milliseconds since epoch of the first trade date."
    )
    priceHint: Optional[int] = Field(None, description="Hint for price precision.")
    regularMarketChangePercent: Optional[float] = Field(
        None, description="Percentage change in regular market price."
    )
    preMarketChange: Optional[float] = Field(
        None, description="Change in pre-market price."
    )
    preMarketChangePercent: Optional[float] = Field(
        None, description="Percentage change in pre-market price."
    )
    preMarketTime: Optional[int] = Field(
        None, description="Timestamp of the pre-market data."
    )
    preMarketPrice: Optional[float] = Field(None, description="Pre-market price.")
    regularMarketChange: Optional[float] = Field(
        None, description="Change in regular market price."
    )
    regularMarketTime: Optional[int] = Field(
        None, description="Timestamp of the regular market data."
    )
    regularMarketPrice: Optional[float] = Field(
        None, description="Regular market price."
    )
    regularMarketDayHigh: Optional[float] = Field(
        None, description="Highest price during the regular market day."
    )
    exchange: Optional[str] = Field(None, description="Exchange identifier.")
    fiftyTwoWeekHigh: Optional[float] = Field(None, description="52-week high price.")
    fiftyTwoWeekLow: Optional[float] = Field(None, description="52-week low price.")
    displayName: Optional[str] = Field(None, description="Display name of the company.")
    symbol: Optional[str] = Field(None, description="Symbol of the company.")


class FincanceScreenerResponse(BaseModel):
    """Complete response from the endpoint."""

    count: int = Field(..., description="Number of results")
    quotes: List[FincanceScreenerResult] = Field(..., description="List of results")


# 2. Data Fetching Function
def fetch_screener_data(params: FincanceScreenerParams) -> FincanceScreenerResponse:
    """
    Fetch data from the endpoint.

    Args:
        params: EndpointParams object containing all query parameters

    Returns:
        EndpointResponse object containing the results

    Raises:
        httpx.HTTPError: If the API request fails
    """

    filter = FincanceScreenerParams().screenerOptions
    screener.set_predefined_body(filter)
    response = screener.response
    return FincanceScreenerResponse(**response)


# 3. Handler Function
async def handle_screenerdata(
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
        response = fetch_screener_data(FincanceScreenerParams(**(arguments or {})))
        return [types.TextContent(type="text", text=str(response))]
    except Exception as e:
        log.error(f"Error handling endpoint: {e}")
        raise


# 4. Tool Registration
TOOLS.append(
    types.Tool(
        name="stock-screendata",
        description="Description of what this endpoint does",
        inputSchema=FincanceScreenerParams.model_json_schema(),
    )
)
TOOLS_HANDLERS["stock-screendata"] = handle_screenerdata


###################
# [Another Endpoint Name]
###################
...

# Server initialization (if module is run directly)
if __name__ == "__main__":
    # import anyio
    #
    # from odmcp.utils import run_server
    #
    # anyio.run(
    #    run_server, "service.name", RESOURCES, RESOURCES_HANDLERS, TOOLS, TOOLS_HANDLERS
    # )
    print(
        "screenerdata",
        fetch_screener_data(FincanceScreenerParams(screenerOptions="top_mutual_funds")),
    )
