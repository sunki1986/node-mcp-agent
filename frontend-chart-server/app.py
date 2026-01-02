import logging
import os

# 1. Setup File Logging only
def setup_file_logger():
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Create a custom logger
    file_logger = logging.getLogger("app_debug")
    file_logger.setLevel(logging.DEBUG)
    
    # Prevent this logger from sending messages to the console/stdout
    file_logger.propagate = False 

    # Create file handler which logs debug messages
    fh = logging.FileHandler("logs/debug.log", mode="a", encoding="utf-8")
    fh.setLevel(logging.DEBUG)

    # Create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # Add the handler to the logger
    file_logger.addHandler(fh)
    return file_logger

# Initialize it
debug_log = setup_file_logger()

import chainlit as cl
import base64
import json
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain.agents import create_agent
from langchain_openai.chat_models import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import ToolMessage, AIMessageChunk, HumanMessage
from langchain_core.runnables import RunnableConfig
 

load_dotenv()

api_key=os.getenv('OPENAI_API_KEY')
mcp_server=os.getenv('mcp_chat_server')


@cl.on_chat_start
async def chart_start():
    agent_prompt = (
        "You are a metrics specialist with two tools (no other tool from public): "
        "1. 'get_metric_timeseries': Use this tool when user requests raw data for a metric. "
        "2. 'render_metric_chart': Use this ONLY when user requests chart or visual. pre-requisite is first tool output i.e. get_metric_timeseries "
    )
    llm=ChatOpenAI(api_key=api_key)

    mcp_client=MultiServerMCPClient(
        {
            "mcp_chart_server":{
                "url":mcp_server
                ,"transport":"streamable_http"
            }
        }
    )
    tools=await mcp_client.get_tools()
    from langchain.agents import create_agent

    agent = create_react_agent(
        model=llm,
        tools=tools,        # if your version supports it
        prompt= agent_prompt  # pass as keyword
    )
    cl.user_session.set('agent',agent)
    cl.user_session.set('chat_history',[])
    # print(llm.invoke('tell me a joke').content)
    await cl.Message(content='App started successfully').send()

@cl.on_message
async def on_message(message: cl.Message):
    agent = cl.user_session.get('agent')
    chat_history = cl.user_session.get('chat_history', [])
    
    # 1. Clean history to ensure no lingering binary data causes a 400 error
    input_messages = []
    for m in chat_history[-5:]:
        role = "user" if m["role"] == "user" else "assistant"
        input_messages.append(HumanMessage(content=f"{role.capitalize()}: {m['content']}"))
    input_messages.append(HumanMessage(content=message.content))

    full_text_response = ""
    text_message = cl.Message(content="")

    try:
        async for chunk, metadata in agent.astream(
            {"messages": input_messages}, 
            config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
            stream_mode="messages"
        ):
            # Handle AI streaming text
            if isinstance(chunk, AIMessageChunk):
                if isinstance(chunk.content, str):
                    full_text_response += chunk.content
                    await text_message.stream_token(chunk.content)

            # --- CRITICAL FIX FOR 400 ERROR ---
            elif isinstance(chunk, ToolMessage):
                try:
                    # Manually parse the MCP tool output
                    content = chunk.content
                    if isinstance(content, str) and content.startswith('['):
                        content = json.loads(content)
                    
                    if isinstance(content, list):
                        text_parts = []
                        for block in content:
                            debug_log.debug(block)
                            if block.get("type") == "image":
                                # 1. Display binary in Chainlit UI ONLY
                                img_data = block.get("base64")
                                img_bytes = base64.b64decode(img_data) if isinstance(img_data, str) else img_data
                                image_el = cl.Image(content=img_bytes, name="mcp_output", display="inline")
                                await cl.Message(content="[Image generated]", elements=[image_el]).send()
                                text_parts.append("[Image displayed to user]")
                            elif block.get("type") == "text":
                                text_parts.append(block.get("text", ""))

                        # 2. STRINGIFY THE TOOL MESSAGE FOR OPENAI
                        # This replaces the complex list with a simple string OpenAI can't reject.
                        chunk.content = "\n".join(text_parts) if text_parts else "Action completed."
                except Exception:
                    chunk.content = "Tool executed successfully." # Fallback to prevent 400
                    
        # 2. Update session with text-only history
        if full_text_response:
            await text_message.send()
            chat_history.append({"role": "user", "content": message.content})
            chat_history.append({"role": "assistant", "content": full_text_response})
            cl.user_session.set('chat_history', chat_history)

    except Exception as e:
        # Final fallback: Clear local state if OpenAI still rejects the message
        if "400" in str(e):
            cl.user_session.set('chat_history', [])
            await cl.ErrorMessage(content="OpenAI rejected the data format. History cleared to restore connection.").send()
        else:
            await cl.ErrorMessage(content=f"An error occurred: {str(e)}").send()
