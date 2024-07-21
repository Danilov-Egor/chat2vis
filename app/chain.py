import os
from dotenv import load_dotenv
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from chains.prompts import router_prompt
from chains.general_chain import general_sql_agent_executor
from chains.visualisation_chain import visualisation_chain
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables from the .env file
load_dotenv()

# Get the OpenAI model from environment variables
OPENAI_MODEL = os.getenv('OPENAI_MODEL')

# Initialize the ChatOpenAI model
llm = ChatOpenAI(temperature=0, model=OPENAI_MODEL)

# Initialize a dictionary to store session histories
store = {}

# Define the router chain
router_chain = router_prompt | llm | StrOutputParser()

# Define the route function
def route(info):
    if "visualisation" in info["request_type"].lower():
        return visualisation_chain
    elif "general" in info["request_type"].lower():
        return general_sql_agent_executor
    else:
        return general_sql_agent_executor

# Define the full chain with routing
full_chain = {
    "request_type": router_chain, 
    "user_prompt": lambda x: x['user_prompt'],
    "chat_history": lambda x: x['chat_history']
} | RunnableLambda(route)

# Function to get session history
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Full chain with message history handling
full_chain_with_message_history = RunnableWithMessageHistory(
    full_chain,
    get_session_history,
    input_messages_key="user_prompt",
    history_messages_key="chat_history",
    verbose=True
)


async def llm_request(user_prompt: str, session_id: str):
    try:
        logger.debug(f"Requesting OpenAI API with prompt: {user_prompt}")
        response = await full_chain_with_message_history.ainvoke(
            {"user_prompt": user_prompt},
            config={"configurable": {"session_id": session_id}},
        )
        logger.debug(f"Response from OpenAI API: {response}")
        return response
    except Exception as e:
        logger.error(f"Error during OpenAI API request: {e}")
        raise
