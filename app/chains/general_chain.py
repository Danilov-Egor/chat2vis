from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.agents.openai_functions_agent.base import create_openai_functions_agent
from .llm_tools import query_db_tool
from .prompts import general_w_sql_prompt
import os
from dotenv import load_dotenv

load_dotenv()


OPENAI_MODEL = os.environ['OPENAI_MODEL']
llm = ChatOpenAI(temperature=0, model=OPENAI_MODEL)


general_sql_agent = create_openai_functions_agent(
    llm=llm,
    prompt=general_w_sql_prompt,
    tools=[query_db_tool]
)

general_sql_agent_executor = AgentExecutor(
    agent=general_sql_agent,
    verbose=True,
    tools=[query_db_tool],
    handle_parsing_errors=True,
    max_iterations=5,
    return_intermediate_steps=True,
)
