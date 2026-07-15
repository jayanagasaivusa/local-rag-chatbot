import asyncio
from langchain_ollama import ChatOllama
from langchain_mcp_adapters.client import MultiServerMCPClient


from langgraph.prebuilt import create_react_agent

async def run_agent():
    # 1. Initialize your local Ollama model
    # Note: Use a model that supports tool calling (e.g., llama3.1, qwen2.5)
    # 1. Initialize your local Ollama model pointing to the host machine
    llm = ChatOllama(
        model="gemma4:12b", 
        temperature=0,
        base_url="http://host.docker.internal:11434" 
    )

    # 2. Connect to your local MCP Server via STDIO
    print("Connecting to MCP Weather Server...")
    client = MultiServerMCPClient({
        "weather": {
            "command": "python",
            "args": ["weather.py"],
            "transport": "stdio",
        }
    })

    # 3. Load the tools dynamically from the server
    tools = await client.get_tools()
    print(f"Loaded tools: {[tool.name for tool in tools]}")

    # 4. Create the Agent
    # We use LangGraph's prebuilt ReAct agent which handles the loop of: 
    # Thought -> Action (Tool Call) -> Observation (Tool Result) -> Answer
    agent = create_react_agent(llm, tools)

    # 5. Test the Agent with a natural language query
    query = "Go to https://thehackernews.com/ and summarize the latest top cybersecurity news headline or story you find there."
    print(f"\nUser: {query}\n")
    
    print("Agent is thinking (and calling tools). Watch it work in real-time:\n")
    print("-" * 40)
    
    # Run the agent using streaming so we can see its steps!
    async for chunk in agent.astream({"messages": [("user", query)]}):
        if "agent" in chunk:
            print("🧠 AI Thought:")
            chunk["agent"]["messages"][0].pretty_print()
        elif "tools" in chunk:
            print("🛠️ Tool Executed:")
            chunk["tools"]["messages"][0].pretty_print()
            
    print("-" * 40)

if __name__ == "__main__":
    asyncio.run(run_agent())