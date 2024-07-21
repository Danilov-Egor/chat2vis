import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
from collections import Counter
import sqlite3
from typing import List, Tuple, Any
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Define the path to the SQLite database from environment variables
DB_PATH = os.getenv('DB_PATH')

def query_sqlite_db(query: str) -> List[Tuple[Any]]:
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
        
        # Execute the query
        cursor.execute(query)
        
        # Fetch all the results
        results = cursor.fetchall()

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

    finally:
        # Close the connection
        if conn:
            conn.close()
    
    return results

def run_code_and_return_object(code_str):
    """
    Executes a given Python code string and returns an object specified in the code.

    Parameters:
    code_str (str): Python code in string format to be executed.

    Returns:
    object: The object specified in the code to be returned.
    """
    local_vars = {}
    global_vars = {
        'plt': plt,
        'query_sqlite_db': query_sqlite_db,
        'datetime': datetime,
        'Counter': Counter
    }  # Include plt and other necessary objects in global variables

    try:
        exec(code_str, global_vars, local_vars)
        return local_vars.get('visualise', lambda: None)()
    except Exception as e:
        print(f"Execution error: {e}")
        return None
