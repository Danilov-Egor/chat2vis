from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.agents.openai_functions_agent.base import create_openai_functions_agent
from .llm_tools import query_db_tool, repl_tool
from .prompts import sql_prompt, python_prompt
import os


# Load the OpenAI model from environment variables
OPENAI_MODEL = os.getenv('OPENAI_MODEL')

# Initialize the ChatOpenAI model
llm = ChatOpenAI(temperature=0, model=OPENAI_MODEL)

# SQL Query Chain
sql_agent = create_openai_functions_agent(
    llm=llm,
    prompt=sql_prompt,
    tools=[query_db_tool]
)

sql_agent_executor = AgentExecutor(
    agent=sql_agent,
    verbose=True,
    tools=[query_db_tool],
    handle_parsing_errors=True,
    max_iterations=5,
    return_intermediate_steps=False,
)

sql_query_chain = (
    {"user_prompt": lambda x: x['user_prompt'], 
     "chat_history": lambda x: x['chat_history']
    } 
    | sql_agent_executor
)

# Python Chain
def clean_code_output_parser(ai_message) -> str:
    """
    Cleans the code output by removing markdown code block delimiters.

    Parameters:
    output (str): The raw output from the LLM.

    Returns:
    str: The cleaned Python code.
    """
    output = ai_message['output']
    if output.startswith("```python"):
        output = output[9:]  # Remove ```python
    if output.endswith("```"):
        output = output[:-3]  # Remove ```
    return {'code': output.strip()}

python_agent = create_openai_functions_agent(
    llm=llm,
    prompt=python_prompt,
    tools=[repl_tool]   
)

python_agent_executor = AgentExecutor(
    agent=python_agent,
    verbose=True,
    tools=[repl_tool],
    handle_parsing_errors=True,
    max_iterations=5,
    return_intermediate_steps=False,
)

python_chat = (
    {"user_prompt": lambda x: x['user_prompt'], 
     "query": lambda x: x['query'], 
     "chat_history": lambda x: x['chat_history']
    }
    | python_agent_executor 
    | clean_code_output_parser
)

# Visualisation Chain
visualisation_chain = (
    sql_query_chain 
    | {'query': lambda x: x['output'], 
       'chat_history': lambda x: x['chat_history'], 
       'user_prompt': lambda x: x['user_prompt']
    } 
    | python_chat
)
