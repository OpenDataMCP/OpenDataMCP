# Open Data Model Context Protocol

![vc3598_Hyper-realistic_Swiss_landscape_pristine_SBB_red_train_p_40803c2e-43f5-410e-89aa-f6bdcb4cd089](https://github.com/user-attachments/assets/80c823dd-0b26-4d06-98f9-5c6d7c9103de)


[![PyPI version](https://badge.fury.io/py/odmcp.svg)](https://badge.fury.io/py/odmcp)
[![CI](https://github.com/grll/OpenDataMCP/actions/workflows/ci.yml/badge.svg)](https://github.com/grll/OpenDataMCP/actions/workflows/ci.yml)
[![GitHub stars](https://img.shields.io/github/stars/grll/OpenDataMCP.svg)](https://github.com/grll/OpenDataMCP/stargazers)
[![License](https://img.shields.io/github/license/grll/OpenDataMCP.svg)](https://github.com/grll/OpenDataMCP/blob/main/LICENSE)

<!--
[![Downloads](https://pepy.tech/badge/odmcp)](https://pepy.tech/project/odmcp)
-->

Open Data MCP connects Large Language Models to open data infrastructures through Anthropic's Open Source Model Context Protocol. This enables any LLMs to provide real-time, data-grounded responses about public services and informations.

## Why Open Data MCP?

- **Rich Data Source**: Access to millions of high-quality public datasets from governments, regions, cities, NGOs...
- **Real-Time Insights**: Get live accurate answers about this data directly in your favorite LLM application.
- **Simple Integration**: Built on Anthropic's Model Context Protocol for seamless LLM integration with any supported clients.
- **Open Architecture**: Designed for community contribution and dataset expansion.

## Key Features

- One-Command setup
- Access to Swiss public datasets (incl. SBB real-time train informations, Weather updates...)
- Compatible with Claude and other MCP-enabled LLMs Application

We maintain a strong focus on reliability, simplicity, and extensibility. Contributions to expand the supported datasets are welcome!

## Usage

### Prerequisites

If you want to use Open Data MCP with Claude Desktop app client you need to install the [Claude Desktop app](https://claude.ai/download).

You will also need `uv` to easily run our CLI and MCP servers.

#### macOS & Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Open Data MCP - CLI Tool

#### Overview

```bash
# show available commands
uvx odmcp 

# show available providers
uvx odmcp list

# show info about a provider
uvx odmcp info $PROVIDER_NAME

# setup a provider's MCP server on your Claude Desktop app
uvx odmcp setup $PROVIDER_NAME

# remove a provider's MCP server from your Claude Desktop app
uvx odmcp remove $PROVIDER_NAME
```

#### Example

Quickstart for the SBB provider:

```bash
uvx odmcp setup sbb
```

## Contributing

We want to scale!

* keep things as simple as possible -> toward AI generated pages keep things in single file
* keep things as standard as possible (TOOLS, TOOLS_HANDLER) and follow the guidelines for what should be a tool, what should be a resource...
* keep it as low as possible in external dependencies (weigh always pros / cons of integrating a new dependency with always a bias toward not adding it)
* keep things formatted with ruff
* keep things tested with pytest
* use typehints and pydantic model for input output of api requests

Concretly:
brew install uv / or other mean to install uv
git clone
uv venv
uv sync
pre-commit install
## Roadmap

data extension
1. integrate as many sources as possible from opendata.swiss

framework extension
1. add support for 

## Limitations
* please oblige to the license must be quoted in commercial application
* please oblige to the license of the data providers

## References
* Model Context Protocol (Anthropic)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
