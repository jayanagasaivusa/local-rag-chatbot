import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # 1. Define how to launch your weather server subprocess
    server_params = StdioServerParameters(
        command="python",
        args=["weather.py"]
    )
    
    # 2. Open the connection via stdio transport
    async with stdio_client(server_params) as (read_stream, write_stream):
        # 3. Create and initialize the client session
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            
            # 4. Ask the server to list its available tools
            response = await session.list_tools()
            print("Available tools discovered:", [tool.name for tool in response.tools])
            
            # 5. Call the specific tool
            print("\nExecuting the weather tool...")
            result = await session.call_tool("get_weather", {"location": "Guntur"})
            
            print("\n--- Result from MCP Server ---")
            # The result content is returned as a list, so we grab the text from the first item
            print(result.content[0].text)

if __name__ == "__main__":
    asyncio.run(main())