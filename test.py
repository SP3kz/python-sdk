import logging

from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client

# disable httpx logs
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("httpcore.http11").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("urllib3.connectionpool").setLevel(logging.CRITICAL)

code = """
import numpy
a = numpy.array([1, 2, 3])
print(a)
a
"""


async def call_tools(session: ClientSession):
    # await session.initialize()
    await session.set_logging_level("debug")
    tools = await session.list_tools()
    print(f"{tools=}")
    result = await session.call_tool("run_python_code", {"python_code": code})
    print(f"{result=}")


async def sse():
    async with sse_client("http://localhost:3001/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await call_tools(session)


async def stdio():
    server_params = StdioServerParameters(
        command="npx",
        args=[
            "--registry=https://registry.npmjs.org",
            "@pydantic/mcp-run-python",
            "stdio",
        ],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await call_tools(session)


if __name__ == "__main__":
    import asyncio

    asyncio.run(sse())
