"""
This experimental client implementation can be used to test your server implementation.
"""

import logging

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

log = logging.getLogger(__name__)

PROVIDER = "ch_sbb"

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="uv",
    args=[
        "run",
        "--package",
        f"odmcp_{PROVIDER}",
        f"packages/odmcp_{PROVIDER}/src/odmcp_ch_sbb.py",
    ],  # Optional command line arguments
    env=None,  # Optional environment variables
)


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            initialize_result = await session.initialize()
            log.info(f"Initialize result: {initialize_result}")

            # List available resources
            # resources = await session.list_resources()

            # # List available prompts
            # prompts = await session.list_prompts()

            # List available tools

            tools = await session.list_tools()
            log.info(f"Tools: {tools}")
            # # Read a resource
            # resource = await session.read_resource("file://some/path")

            # # Call a tool
            # result = await session.call_tool("tool-name", arguments={"arg1": "value"})

            # # Get a prompt
            # prompt = await session.get_prompt(
            #     "prompt-name", arguments={"arg1": "value"}
            # )


if __name__ == "__main__":
    import anyio

    logging.basicConfig(level=logging.DEBUG)

    anyio.run(main)
