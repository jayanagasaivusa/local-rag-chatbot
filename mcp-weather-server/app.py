import asyncio
import gradio as gr
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

async def handle_agent_chat(message, history):
    """Handles the chat interaction using the official LangChain MCP adapter"""
    
    # 1. Connect to your local MCP Server (Just like in test_agent.py!)
    client = MultiServerMCPClient({
        "my_tools": {
            "command": "python",
            "args": ["weather.py"],
            "transport": "stdio",
        }
    })
    
    # 2. Automatically load and wrap the tools
    tools = await client.get_tools()
    
    # 3. Initialize your Windows Ollama instance
    llm = ChatOllama(
        model="gemma4:12b",
        temperature=0,
        base_url="http://host.docker.internal:11434"
    )
    
    # 4. Create the LangGraph Agent
    agent = create_react_agent(llm, tools)
    
    # 5. Run the agent and capture the final response
    response_text = ""
    async for chunk in agent.astream({"messages": [("user", message)]}):
        if "agent" in chunk:
            # We grab the content from the AI's final synthesis step
            response_text = chunk["agent"]["messages"][0].content
            
    return response_text

def chat_interface(message, history):
    """Wrapper function to handle async code inside Gradio's UI"""
    return asyncio.run(handle_agent_chat(message, history))

# --- Gradio UI Layout ---
demo = gr.ChatInterface(
    fn=chat_interface,
    title="🤖 Vignatrix MCP Multi-Tool Agent",
    description="Ask me about the weather in any city, or give me a website URL to summarize!",
    examples=[
        "What is the weather like in Guntur today? Do I need an umbrella?",
        "Go to https://thehackernews.com/ and give me a summary of the latest headline."
    ]
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)