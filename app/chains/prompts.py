from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder


db_schema = """Artist: ArtistID, Name
Playlist: PlaylistID, Name
Employee: EmployeeID, LastName, FirstName, Title, ReportsTo, BirthDate, HireDate, Address, City, State, Country, PostalCode, Phone, Fax, Email
Album: AlbumID, Title, ArtistID
PlaylistTrack: PlaylistID, TrackID
Customer: CustomerID, FirstName, LastName, Company, Address, City, State, Country, PostalCode, Phone, Fax, Email, SupportRepID
Track: TrackID, Name, AlbumID, MediaTypeID, GenreID, Composer, Milliseconds, Bytes, UnitPrice
InvoiceLine: InvoiceLineID, InvoiceID, TrackID, UnitPrice, Quantity
Invoice: InvoiceID, CustomerID, InvoiceDate, BillingAddress, BillingCity, BillingState, BillingCountry, BillingPostalCode, Total
MediaType: MediaTypeID, Name
Genre: GenreID, Name"""

sql_system_prompt = f"""You are a helpful AI assistant that writes SQLite queries. 
You must return only SQLite query. 
Chinook SQLite Database schema: {db_schema}"""

python_system_prompt = f"""You are an AI assistant that writes python function named `visualise` to visualise data.
You have to output only python function that returns matplotlib figure object.
You must use the predefined query_sqlite_db function to query SQLite database and get data.
You must assume that this function is given to you.
def query_sqlite_db(query: str) -> List[Tuple[Any]]:
    \"\"\"
    Runs a read-only query on the specified SQLite database and returns the results.

    :param query: The SQL query to run.
    :return: List of tuples containing the query results.
    \"\"\"
Your goal is to write python function to visualise the data.
Only output a single python function: 
def visualise():
    data = query_sqlite_db(...)
    
    # your implementation
    ...
    
    return fig"""

general_sql_system_prompt = f"""You are a helpful assistant.

You are designed to answer general questions and questions related to the Chinook SQLite database.

The SQLite database schema is as follows:
{db_schema}.

You can use the query_sqlite_db_tool to run SQLite queries and answer the user's questions.
"""

router_prompt_human_template = """Given the user question below, classify it as either `General` or `Visualisation`.

A `Visualisation` question could ask to create a visualisation, modify it (change formatting, color, axes names, size, etc.), or ask a follow-up question based on the previous conversation.

A `General` question will ask for information independent of anything else. For example: "How many tables are there?" or "How many employees are there?"

Do not respond with more than one word.

<question>
{user_prompt}
</question>

Classification:"""

sql_prompt = ChatPromptTemplate(
    input_variables=['user_prompt', 'chat_history'],
    messages=[
        SystemMessagePromptTemplate.from_template(f"""You are a helpful AI assistant that writes SQL queries. 
You must return only SQL query. 
SQLite Database schema: {db_schema}.
Before returning the SQLite query, make sure it is errorless"""),
        MessagesPlaceholder(variable_name='chat_history'),
        HumanMessagePromptTemplate.from_template("Output Only `query`. `query` is an SQLite query that will answer the following question: {user_prompt}. If the question asks to change something in the user request, but is not possible to implement it in SQL, return the unchanged query from the previous step."),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ]
)

python_prompt = ChatPromptTemplate(
    input_variables=['user_prompt', 'query', 'chat_history'],
    messages=[
        SystemMessagePromptTemplate.from_template(python_system_prompt),
        MessagesPlaceholder(variable_name='chat_history'),
        HumanMessagePromptTemplate.from_template("""Output only the `visualise` Python function that will create the following visualization: {user_prompt}. Use the query_sqlite_db() function with query={query} to get data.
Start your answer with: def visualise(): ...
"""),  #  Before returning, test the function by calling it with the help of the python_repl tool: visualise()
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ]
)

general_w_sql_prompt = ChatPromptTemplate(
    input_variables=['user_prompt', 'chat_history'],
    messages=[
        SystemMessagePromptTemplate.from_template(general_sql_system_prompt),
        MessagesPlaceholder(variable_name='chat_history'),
        HumanMessagePromptTemplate.from_template("You might want to use the query_sqlite_db_tool, which runs SQLite queries, if the question is regarding the database. If any errors occur, try fixing them and running the query again. Answer the following question: {user_prompt}."),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ]
)

router_prompt = ChatPromptTemplate(
    input_variables=['user_prompt', 'chat_history'],
    messages=[
        MessagesPlaceholder(variable_name='chat_history'),
        HumanMessagePromptTemplate.from_template(router_prompt_human_template),
    ]
)