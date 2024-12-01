from unittest.mock import patch

import pytest
from click.testing import CliRunner

from odmcp.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_run_valid_provider(runner):
    # TODO: Implement this test
    pass


def test_run_invalid_provider(runner):
    result = runner.invoke(cli, ["run", "nonexistent_provider"])
    assert result.exit_code == 1
    assert "Provider 'nonexistent_provider' not found." in result.output


def test_list_providers(runner):
    mock_distributions = [
        type("Distribution", (), {"metadata": {"Name": "odmcp_provider1"}}),
        type("Distribution", (), {"metadata": {"Name": "odmcp_provider2"}}),
    ]
    with patch("importlib.metadata.distributions") as mock_dist:
        mock_dist.return_value = mock_distributions

        result = runner.invoke(cli, ["list"])

        assert result.exit_code == 0
        assert "Available providers:" in result.output
        assert "provider1" in result.output
        assert "provider2" in result.output


def test_list_no_providers(runner):
    with patch("importlib.metadata.distributions") as mock_dist:
        mock_dist.return_value = []  # No providers installed

        result = runner.invoke(cli, ["list"])

        assert result.exit_code == 0
        assert "No providers available" in result.output
        assert "Install providers with:" in result.output
        assert "uv pip install odmcp[provider_name]" in result.output


def test_info_valid_provider(runner):
    mock_module = type(
        "Module",
        (),
        {"__doc__": "Test provider description", "SUPPORTED_TYPES": ["type1", "type2"]},
    )

    with patch("importlib.import_module") as mock_import:
        mock_import.return_value = mock_module

        result = runner.invoke(cli, ["info", "test_provider"])

        assert result.exit_code == 0
        assert "Provider: test_provider" in result.output
        assert "Description: Test provider description" in result.output
        assert "Supported types: type1, type2" in result.output


def test_info_invalid_provider(runner):
    result = runner.invoke(cli, ["info", "nonexistent_provider"])
    assert result.exit_code == 1
    assert "Provider 'nonexistent_provider' not found" in result.output


def test_version_command(runner):
    with patch("importlib.metadata.version") as mock_version:
        mock_version.return_value = "1.0.0"

        result = runner.invoke(cli, ["version"])

        assert result.exit_code == 0
        assert "odmcp version: 1.0.0" in result.output
