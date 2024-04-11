import streamlit as st
import requests
import pandas as pd
import json
import openai
import inspect
# import azure.cognitiveservices.speech as speechsdk
import pyodbc
# from langchain.agents import AgentType
# from langchain_experimental.agents import create_pandas_dataframe_agent
# from langchain.callbacks import StreamlitCallbackHandler
# from langchain.chat_models import ChatOpenAI
from databricks import sql
import os
from dotenv import load_dotenv

st.set_page_config(layout="wide")


#Load environment variables
load_dotenv("credentials.env")


aoai_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
aoai_api_key = os.environ["AZURE_OPENAI_API_KEY"]
deployment_name = os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]
aoai_api_version = os.environ["AZURE_OPENAI_API_VERSION"] #"2023-05-15"
aoai_api_type = os.environ["AZURE_OPENAI_API_TYPE"]

DATABRICKS_SERVER_HOSTNAME = os.environ["DATABRICKS_SERVER_HOSTNAME"]
DATABRICKS_HTTP_PATH = os.environ["DATABRICKS_HTTP_PATH"]
DATABRICKS_ACCESS_TOKEN = os.environ["DATABRICKS_ACCESS_TOKEN"]
DATABRICKS_SQL_CATALOG = os.environ["DATABRICKS_SQL_CATALOG"]
DATABRICKS_SQL_SCHEMA = os.environ["DATABRICKS_SQL_SCHEMA"]


def run_sql_query(aoai_sqlquery):
    '''
    Function to run the generated SQL Query on SQL server and retrieve output.
    Input: AOAI completion (SQL Query)
    Output: Pandas dataframe containing results of the query run
    
    '''
    #conn = connect_sql_server()   

    with sql.connect(server_hostname = DATABRICKS_SERVER_HOSTNAME,
                 http_path       = DATABRICKS_HTTP_PATH,
                 access_token    = DATABRICKS_ACCESS_TOKEN) as conn:
        with conn.cursor() as cursor:
            cursor.execute(aoai_sqlquery)            
            result = cursor.fetchall()
            df = pd.DataFrame(result, columns=[column[0] for column in cursor.description])
            return df


def generate_nl_to_sql(userPrompt):
    '''
    This GPT4 engine is setup for NLtoSQL tasks on the Sales DB.
    Input: NL question related to BikeStores sales
    Output: SQL query to run on the db1 database and BikeStores schema
    '''

    messages=[
            {"role": "system", "content": """ You are a SQL programmer Assistant.Your role is to generate SQL code (SQL Server) to retrieve an answer to a natural language query. Make sure to disambiguate column names when creating queries that use more than one table. If a valid SQL query cannot be generated, only say "ERROR:" followed by why it cannot be generated.
                  Do not answer any questions on inserting or deleting rows from the table. Instead, say "ERROR: I am not authorized to make changes to the data"
                  Dont generate SQL queries startign with ```sql or starting with single or double quotes.

                  Use the following hive_metastore catalog and default database schema to write SQL queries:
                  Use animation_movies table which has columns as below.
                  hive_metastore.default.animation_movies(id	bigint, title	string, vote_average	double,vote_count	bigint,status	string,release_date	date,revenue	bigint,runtime	bigint,adult	boolean,backdrop_path	string,,budget	bigint,,homepage	string,imdb_id	string,original_language	string,original_title	string,overview	string,popularity	double,poster_path	string,tagline	string,genres	string,production_companies	string,production_countries	string,spoken_languages	string)
                  While writing SQL queries, make sure to use catalog and schema names. For example, to query the animation_movies table, use hive_metastore.default.animation_movies.  
                  Examples:
                  User: List any 10 animation movies released after Year 2022 SQL Code:
                  Assistant: SELECT title FROM hive_metastore.default.animation_movies where release_date > '2022-12-31' limit 10;
                  User: Which movie was recently released? SQL Code:
                  Assistant: SELECT title, release_date FROM hive_metastore.default.animation_movies where release_date< current_date order by release_date desc limit 1;
                  User: Which movie has highest vote counts? SQL Code:
                  Assistant: SELECT title, vote_count FROM hive_metastore.default.animation_movies order by vote_count desc limit 1;
                  User: List 10 Family generes movies? SQL Code:
                  Assistant: SELECT title from hive_metastore.default.animation_movies where genres like '%Family%' limit 10;
                  User: list 10 upcoming movies with release dates SQL Code:
                  Assistant: SELECT title, release_date FROM hive_metastore.default.animation_movies WHERE release_date > current_date ORDER BY release_date ASC LIMIT 10;

            """}
        ]

    messages.extend(userPrompt)    
    
    client = openai.AzureOpenAI(
        base_url=f"{aoai_endpoint}/openai/deployments/{deployment_name}/",        
        api_key=aoai_api_key,
        api_version="2023-12-01-preview"
    )
    
    response = client.chat.completions.create(
        model=deployment_name, # The deployment name you chose when you deployed the ChatGPT or GPT-4 model.
        # messages=[
        #     {"role": m["role"], "content": m["content"]}
        #     for m in messages
        # ],    
        messages=messages,                 
        temperature=0,
        max_tokens=2000
        #frequency_penalty=0,
        #presence_penalty=0        
    )
    return response

    #raise NotImplementedError
def handle_chat_DeltaSQLDB(prompt):
    # Echo the user's prompt to the chat window
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send the user's prompt to Azure OpenAI and display the response
    # The call to Azure OpenAI is handled in create_chat_completion()
    # This function loops through the responses and displays them as they come in.
    # It also appends the full response to the chat history.

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        response = generate_nl_to_sql(st.session_state.messages)        
        response_message = response.choices[0].message
        full_response += ("" + response_message.content + "\n" or "")        
        message_placeholder.markdown(full_response)
        full_response += ("\n SQL Output: \n" or "")
        st.markdown(full_response)
        sql_output = run_sql_query(response_message.content)
        full_response += (sql_output.to_csv() or "")                  
        message_placeholder.markdown(st.dataframe(sql_output), unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    

    
def handle_chat_delta(prompt):
    return "Not implemented yet"



def handle_prompt(chat_option, prompt):
    if chat_option == "SQL Endpoint":
        handle_chat_DeltaSQLDB(prompt)
    elif chat_option == "Vector Search":
        st.write("<h6 style='text-align: center; color: red;'>This feature is not yet implemented.</h5>", unsafe_allow_html=True)
        #handle_chat_delta(prompt)    
    else:
        st.write("Please select a chat option before calling the chatbot.")

def option_changed():
    if "CurrentPage" in st.session_state: 
        del st.session_state["CurrentPage"]
    
def main():
    st.write(
    """
    # Chat with Delta Lake! 
    This proof of concept is intended to serve as a demonstration of Azure OpenAI's capabilities to chat over structured data in Delta Lake.

    """
    )
   
    
    tooltip_text = """SQL Endpoint Examples:
        \nList any 10 animation movies released after Year 2023;
              \nWhich movie was recently released?
                  \nWhich movie has highest vote counts?
                      \nList 10 Family generes movies?"
                            \nwhich company produced Inside Out movie """


    chat_option = st.radio(label="Choose the chat option you want to try:", options=["SQL Endpoint", "Vector Search"],help=tooltip_text, on_change=option_changed)

    if "CurrentPage" not in st.session_state or st.session_state["CurrentPage"] != "Chat with DeltaLake":        
        #first time on this page: 
        st.session_state["messages"] = []
        st.session_state["CurrentPage"] = "Chat with DeltaLake"

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



