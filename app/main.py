import asyncio
import matplotlib.pyplot as plt
import streamlit as st
import uuid
from datetime import datetime
from collections import Counter
from chain import llm_request
from helper import run_code_and_return_object

# Suppress Streamlit deprecation warning for pyplot
st.set_option('deprecation.showPyplotGlobalUse', False)
st.set_page_config(page_title="Chat 2 Visualisation", layout="wide")

# Error string
error_str = "Sorry, I encountered a problem with your request. Please try asking a more direct question."

# CSS to hide Streamlit UI elements
st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)

# Function to process the prompt and get structured output
async def handle_prompt(prompt, session_id):
    response = await llm_request(prompt, session_id)
    answer = {}

    if 'code' in response:
        # Generate the figure from the response code
        try:
            fig = run_code_and_return_object(response['code'])
            answer['figure'] = fig
            answer['code'] = response['code']
        except Exception as e:
            print('Exception:', e)
            answer['content'] = error_str

    if 'output' in response:
        answer['content'] = response['output']

    # Fallback
    if len(answer.keys()) == 0:
        answer['content'] = error_str

    return answer

# Function to generate session ID
def generate_session_id():
    return str(uuid.uuid4())

# Initialize message history in session state if not already present
if "messages" not in st.session_state:
    st.session_state.messages = []

# Check if the session ID is already in the session state
if 'session_id' not in st.session_state:
    st.session_state['session_id'] = generate_session_id()

# Define a variable to enable/disable chat_input()
if 'is_chat_input_disabled' not in st.session_state:
    st.session_state['is_chat_input_disabled'] = False

# Set the title of the Streamlit app
st.title("Chat 2 Visualisation")

st.markdown("""
The [Chinook Database](https://github.com/lerocha/chinook-database?tab=readme-ov-file) is a sample database. It represents a digital media store, including tables for artists, albums, media tracks, invoices, and customers.  *Developed by Egor*
""")

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "content" in message:
            st.markdown(message["content"])

        if "code" in message:
            with st.expander("See code"):
                st.code(message["code"])

        if "figure" in message:
            st.pyplot(message["figure"], )

# Handle user input and process the prompt
prompt = st.chat_input("How can I help?", max_chars=150, disabled=st.session_state['is_chat_input_disabled'])

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state['is_chat_input_disabled'] = True
    st.rerun()

if st.session_state['is_chat_input_disabled']:
    # Run the async function to get the response
    response = asyncio.run(handle_prompt(st.session_state.messages[-1]['content'], st.session_state['session_id']))

    with st.chat_message('assistant'):
        if 'code' in response:
            st.session_state.messages.append({
                "role": "assistant",
                "code": response['code'],
            })
            with st.expander("See code"):
                st.code(response["code"])

        if 'figure' in response:
            st.session_state.messages.append({
                "role": "assistant",
                "figure": response['figure'],
            })
            st.pyplot(response["figure"])

        if 'content' in response:
            st.session_state.messages.append({
                "role": "assistant",
                "content": response['content'],
            })
            st.markdown(response["content"])

    st.session_state['is_chat_input_disabled'] = False
    st.rerun()
