from langchain.agents import Tool
from langchain_experimental.utilities import PythonREPL
import sqlite3
from typing import List, Tuple, Any
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

DB_PATH = os.getenv('DB_PATH')

##### SQLite TOOL #####
def query_sqlite_db_tool(query: str) -> List[Tuple[Any]]:
    """
    Runs a read-only query on the specified SQLite database and returns the results.

    :param query: The SQL query to run.
    :return: List of tuples containing the query results.
    """
    results = []
    try:
        # Connect to the SQLite database in read-only mode
        conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)
        cursor = conn.cursor()

        # Execute the query with parameters
        cursor.execute(query)
        
        # Fetch all the results
        results = cursor.fetchall()
        
        keep_first = 10

        if len(results) <= keep_first:
            return results
        else:
            return [f'First {keep_first} elements: {results[:10]}']
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return [(f"SQLite error: {e}")]
    
    finally:
        # Close the connection
        if conn:
            conn.close()

query_db_tool = Tool.from_function(
    name=query_sqlite_db_tool.__name__,
    func=query_sqlite_db_tool,
    description='Runs a read-only query on the SQLite database and returns the results.'
)

##### PYTHON REPL TOOL #####
python_repl = PythonREPL()
repl_tool = Tool(
    name="python_repl",
    func=python_repl.run,
    description="A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with `print(...)`.",
)
