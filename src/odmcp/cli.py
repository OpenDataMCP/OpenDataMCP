import importlib
import json
import os
import platform
import sys
from pathlib import Path

import anyio
import click


@click.group()
def cli():
    """OpenDataMCP CLI tool"""
    pass


@cli.command()
@click.argument("provider")
def run(provider: str):
    """Run a specific provider MCP server."""
    try:
        module = importlib.import_module(f"odmcp.providers.{provider}")
        anyio.run(module.main)
    except ImportError:
        click.echo(f"Provider '{provider}' not found.")
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error running provider: {e}")
        sys.exit(1)


@cli.command()
def list():
    """List all available providers"""
    try:
        from importlib.metadata import distributions

        # Find all installed packages starting with odmcp_
        providers = [
            dist.metadata["Name"].replace("odmcp_", "")
            for dist in distributions()
            if dist.metadata["Name"].startswith("odmcp_")
        ]

        if not providers:
            click.echo("No providers available. Install providers with:")
            click.echo("uv pip install odmcp[provider_name]")
            return

        click.echo("Available providers:")
        for provider in sorted(providers):
            click.echo(f"  - {provider}")
    except Exception as e:
        click.echo(f"Error listing providers: {e}")
        sys.exit(1)


@cli.command()
@click.argument("provider")
def info(provider: str):
    """Show detailed information about a provider"""
    try:
        module = importlib.import_module(f"odmcp_{provider}")

        click.echo(f"Provider: {provider}")
        if hasattr(module, "__doc__") and module.__doc__:
            click.echo(f"Description: {module.__doc__.strip()}")
        if hasattr(module, "SUPPORTED_TYPES"):
            click.echo(f"Supported types: {', '.join(module.SUPPORTED_TYPES)}")
    except ImportError:
        click.echo(f"Provider '{provider}' not found. Make sure it's installed with:")
        click.echo(f"uv pip install 'odmcp[{provider}]'")
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error getting provider info: {e}")
        sys.exit(1)


@cli.command()
def version():
    """Show the odmcp version"""
    try:
        from importlib.metadata import version as get_version

        try:
            ver = get_version("odmcp")
        except importlib.metadata.PackageNotFoundError:
            # Fallback to reading version from __init__.py
            from odmcp import __version__ as ver
        click.echo(f"odmcp version: {ver}")
    except Exception as e:
        click.echo(f"Error getting odmcp version: {e}")
        sys.exit(1)


@cli.command()
@click.argument("provider")
def setup(provider: str):
    """Setup the MCP server for use with Claude Desktop"""
    # Check platform
    system = platform.system()
    if system not in ["Darwin", "Windows"]:
        click.echo("This command is only supported on Windows and macOS")
        sys.exit(1)

    # Determine config path
    if system == "Darwin":
        config_path = (
            Path.home()
            / "Library/Application Support/Claude/claude_desktop_config.json"
        )
    else:  # Windows
        config_path = Path(os.getenv("APPDATA")) / "Claude/claude_desktop_config.json"

    # Check if config directory exists
    if not config_path.parent.exists():
        click.echo(
            f"Couldn't find Claude configuration directory at {config_path.parent}. Have you installed the Claude Desktop app?"
        )
        sys.exit(1)

    # Create config file if it doesn't exist
    if not config_path.exists():
        with open(config_path, "w") as f:
            json.dump({}, f, indent=2)

    try:
        # Read existing config
        with open(config_path, "r") as f:
            config = json.load(f)

        # Add or update mcpServers entry
        if "mcpServers" not in config:
            config["mcpServers"] = {}

        # TODO: add support for env variables
        config["mcpServers"][provider] = {
            "command": "uvx",
            "args": ["odmcp", "run", provider],
        }

        # Write updated config
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        click.echo(
            f"Successfully configured MCP server for provider '{provider}'. You can now restart Claude Desktop."
        )

    except Exception as e:
        click.echo(f"Error updating config file: {e}")
        sys.exit(1)


@cli.command()
@click.argument("provider")
def remove(provider: str):
    """Remove MCP server configuration for a provider"""
    # Check platform
    system = platform.system()
    if system not in ["Darwin", "Windows"]:
        click.echo("This command is only supported on Windows and macOS")
        sys.exit(1)

    # Determine config path
    if system == "Darwin":
        config_path = (
            Path.home()
            / "Library/Application Support/Claude/claude_desktop_config.json"
        )
    else:  # Windows
        config_path = Path(os.getenv("APPDATA")) / "Claude/claude_desktop_config.json"

    # Check if config file exists
    if not config_path.exists():
        click.echo(
            f"Couldn't find claude_desktop_config.json at {config_path}. Have you installed the Claude Desktop app?"
        )
        sys.exit(1)

    try:
        # Read existing config
        with open(config_path, "r") as f:
            config = json.load(f)

        # Check if mcpServers exists and provider is configured
        if "mcpServers" not in config or provider not in config["mcpServers"]:
            click.echo(f"Provider '{provider}' is not configured")
            return

        # Remove the provider
        del config["mcpServers"][provider]

        # Remove mcpServers if it's empty
        if not config["mcpServers"]:
            del config["mcpServers"]

        # Write updated config
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        click.echo(
            f"Successfully removed MCP server configuration for provider '{provider}'. You can now restart Claude Desktop."
        )

    except Exception as e:
        click.echo(f"Error updating config file: {e}")
        sys.exit(1)


def main():
    cli()


if __name__ == "__main__":
    main()
