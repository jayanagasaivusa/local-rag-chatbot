import httpx
from bs4 import BeautifulSoup

from mcp.server.fastmcp import FastMCP

# 1. Initialize the FastMCP server
# This object acts as the container for all your tools.
mcp = FastMCP("MyTools")

# 2. Add a tool using the decorator
# Tools are functions that an LLM can execute.
# By decorating it with @mcp.tool, FastMCP automatically handles the schema and protocol details.
@mcp.tool()
async def get_weather(location: str) -> str:
    """Gets the current weather for a specific city (e.g., 'Delhi', 'London')."""
    try:
        url = f"https://wttr.in/{location}?format=3"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return f"Weather Update: {response.text.strip()}"
    except Exception as e:
        return f"Error fetching weather: {str(e)}"
    


@mcp.tool()
async def read_website(url: str) -> str:
    """Reads the text from a website or news article so it can be summarized."""
    try:
        async with httpx.AsyncClient() as client:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = await client.get(url, headers=headers, follow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # UPGRADE: Now we search for headings AND paragraphs!
            elements = soup.find_all(['h1', 'h2', 'h3', 'p'])
            text = "\n".join([el.get_text().strip() for el in elements if el.get_text().strip()])
            
            return f"Website Content:\n{text[:5000]}"
            
    except Exception as e:
        return f"Error reading website: {str(e)}"

if __name__ == "__main__":
    # 3. Run the server
    # This defaults to the 'stdio' transport, which is the traditional way to connect MCP servers to clients.
    mcp.run()