import streamlit as st
import requests
import pandas as pd
import json
import openai
import inspect
import azure.cognitiveservices.speech as speechsdk
import pyodbc
from langchain.agents import AgentType
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

st.set_page_config(layout="wide")

# with open('config.json') as f:
#     config = json.load(f)
#Load environment variables
load_dotenv("credentials.env")

aoai_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
aoai_api_key = os.environ["AZURE_OPENAI_API_KEY"]
deployment_name = os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]
aoai_api_version = os.environ["AZURE_OPENAI_API_VERSION"] #"2023-05-15"


def classify_embeddings(prompt):
    return ""
def classify_finetuning(prompt):
    return ""

def handle_prompt(chat_option, prompt):
    if chat_option == "Embeddings":
        st.write("<h6 style='text-align: center; color: red;'>This feature is not yet implemented.</h5>", unsafe_allow_html=True)
        #classify_embeddings(prompt)
    elif chat_option == "Fine Tuning":
        st.write("<h6 style='text-align: center; color: red;'>This feature is not yet implemented.</h5>", unsafe_allow_html=True)
        #classify_finetuning(prompt)    
    else:
        st.write("Please select a chat option before calling the chatbot.")

def main():
    st.session_state.messages = []
    st.write(
    """
    # NL Text Classification! 
    This proof of concept is intended to serve as a demonstration of classification use cases using various approaches.

    """
    )

    chat_option = st.radio(label="Choose the chat option you want to try:", options=["Embeddings", "Fine Tuning"])

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    
    # Await a user message and handle the chat prompt when it comes in.
    if prompt := st.chat_input("Enter a message:"):
        handle_prompt(chat_option, prompt)

if __name__ == "__main__":
    main()


