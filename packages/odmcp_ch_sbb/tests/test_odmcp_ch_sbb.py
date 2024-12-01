import pytest
from unittest.mock import patch, Mock

from odmcp_ch_sbb import (
    fetch_rail_traffic_info,
    TrafficInfoParams,
    handle_rail_traffic_info,
)


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def mock_traffic_info_response():
    return {
        "total_count": 2,
        "results": [
            {
                "title": "Track maintenance in Zürich",
                "link": "https://data.sbb.ch/info/1",
                "description": "Maintenance work between Zürich HB and Oerlikon",
                "published": "2024-01-01T10:00:00Z",
                "author": "SBB",
                "validitybegin": "2024-01-02T00:00:00Z",
                "validityend": "2024-01-03T00:00:00Z",
                "description_html": "<p>Maintenance work between Zürich HB and Oerlikon</p>",
            },
            {
                "title": "Delays in Bern",
                "link": "https://data.sbb.ch/info/2",
                "description": "Signal failure causing delays",
                "published": "2024-01-01T11:00:00Z",
                "author": "SBB",
                "validitybegin": "2024-01-01T11:00:00Z",
                "validityend": "2024-01-01T15:00:00Z",
                "description_html": "<p>Signal failure causing delays</p>",
            },
        ],
    }


def test_fetch_rail_traffic_info(mock_traffic_info_response):
    with patch("httpx.get") as mock_get:
        mock_get.return_value.json.return_value = mock_traffic_info_response
        mock_get.return_value.raise_for_status = Mock()

        params = TrafficInfoParams(limit=2, timezone="Europe/Zurich")
        response = fetch_rail_traffic_info(params)

        assert response.total_count == 2
        assert len(response.results) == 2
        assert response.results[0].title == "Track maintenance in Zürich"
        assert response.results[1].title == "Delays in Bern"


@pytest.mark.anyio
async def test_handle_rail_traffic_info(mock_traffic_info_response):
    with patch("httpx.get") as mock_get:
        mock_get.return_value.json.return_value = mock_traffic_info_response
        mock_get.return_value.raise_for_status = Mock()

        result = await handle_rail_traffic_info({"limit": 2})

        assert len(result) == 1
        assert result[0].type == "text"
        assert "Track maintenance in Zürich" in result[0].text
        assert "Delays in Bern" in result[0].text
