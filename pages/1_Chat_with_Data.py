import streamlit as st
import requests
import pandas as pd
import json
import openai
import inspect
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
import os

st.set_page_config(layout="wide")

#Load environment variables
load_dotenv("credentials.env")

aoai_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
aoai_api_key = os.environ["AZURE_OPENAI_API_KEY"]
deployment_name = os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]
aoai_api_version = os.environ["AZURE_OPENAI_API_VERSION"]

speech_key = os.environ["AI_SPEECH_KEY"]
speech_region = os.environ["AI_SPEECH_REGION"]
contoso_webservice_base_url = os.environ["CONTOSO_WEBSERVICE_BASE_URL"]

ai_search_endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
ai_search_key = os.environ["AZURE_SEARCH_KEY"]
ai_search_Contososuites_Index = os.environ["AZURE_SEARCH_CONTOSUITES_INDEX"]


### 02: Chat with customer data
def create_chat_completion(deployment_name, messages, endpoint, key, index_name):
    # Create an Azure OpenAI client. We create it in here because each exercise will
    # require at a minimum different base URLs.

    client = openai.AzureOpenAI(        
        base_url=f"{aoai_endpoint}/openai/deployments/{deployment_name}/extensions/",
        api_key=aoai_api_key,
        api_version=aoai_api_version
    )
    
    # Create and return a new chat completion request
    # Be sure to include the "extra_body" parameter to use Azure AI Search as the data source
    #this is Azure Open AI On your data feature

    return client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": m["role"], "content": m["content"]}
            for m in messages
        ],
        stream=True,
        extra_body={
            "dataSources": [
                {
                    "type": "AzureCognitiveSearch",
                    "parameters": {
                        "endpoint": endpoint,
                        "key": key,
                        "indexName": index_name,
                    }
                }
            ]
        }
    )
    
    
    #raise NotImplementedError

def handle_chat_prompt(prompt):
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
        for response in create_chat_completion(deployment_name, st.session_state.messages, ai_search_endpoint, ai_search_key, ai_search_Contososuites_Index):
            full_response += (response.choices[0].delta.content or "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    #raise NotImplementedError

### 03: Function calls
def get_customers(search_criterion, search_value):
    full_server_url = f"{contoso_webservice_base_url}/Customer/?searchCriterion={search_criterion}&searchValue={search_value}"
    r = requests.get(
        full_server_url,
        headers={"Content-Type": "application/json"}
    )
    if r.status_code == 200:
        st.write(pd.read_json(r.content.decode("utf-8")))
        return r.content.decode("utf-8")
    else:
        return f"Failure to find any customers with {search_criterion} {search_value}."

#  function call definition
functions = [
      {
          "name": "get_customers",
          "description": "Get a list of customers based on some search criterion.",
          "parameters": {
              "type": "object",
              "properties": {
                  "search_criterion": {"type": "string", "enum": ["CustomerName", "LoyaltyTier", "DateOfMostRecentStay"]},
                  "search_value": {"type": "string"},
              },
              "required": ["search_criterion", "search_value"],
          },
      }
  ]
available_functions = {
    "get_customers": get_customers,
}

def create_chat_completion_with_functions(deployment_name, messages):
    # Create an Azure OpenAI client. We create it in here because each exercise will
    # require at a minimum different base URLs.
    client = openai.AzureOpenAI(
        base_url=f"{aoai_endpoint}/openai/deployments/{deployment_name}/",
        api_key=aoai_api_key,
        api_version=aoai_api_version
    )
    # Create and return a new chat completion request
    # Be sure to include the "functions" parameter and set "function_call"
    return client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": m["role"], "content": m["content"]}
            for m in messages
        ],
        functions=functions,
        function_call="auto",
    )
    
    #raise NotImplementedError

def handle_chat_prompt_with_functions(prompt):
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
        response = create_chat_completion_with_functions(deployment_name, st.session_state.messages)
        response_message = response.choices[0].message

        # Check if GPT returned a function call
        if response_message.function_call:
            # Get the function name and arguments
            function_name = response_message.function_call.name
            # Verify the function
            if function_name not in available_functions:
                full_response = f"Sorry, I don't know how to call the function `{function_name}`."
            else:
                function_to_call = available_functions[function_name]
                full_response = f"Calling function '{function_name}'...\n"
                # Verify the function has the correct number of arguments
                function_args = json.loads(response_message.function_call.arguments)
                if check_args(function_to_call, function_args) is False:
                    full_response += f"\n Sorry, I don't know how to call the function `{function_name}` with those arguments."
                else:
                    # Call the function
                    full_response += "  \n  Response: " + function_to_call(**function_args)
    message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    #raise NotImplementedError

# helper method used to check if the correct arguments are provided to a function
def check_args(function, args):
    sig = inspect.signature(function)
    params = sig.parameters

    # Check if there are extra arguments
    for name in args:
        if name not in params:
            return False
    # Check if the required arguments are provided 
    for name, param in params.items():
        if param.default is param.empty and name not in args:
            return False

    return True


###  This function will recognize voice from microphone
def recognize_from_microphone(speech_key, speech_region, speech_recognition_language="en-US"):
    # Create an instance of a speech config with specified subscription key and service region.
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.speech_recognition_language=speech_recognition_language

    # Create a microphone instance and speech recognizer.
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    # Start speech recognition
    print("Speak into your microphone.")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    # Check the result
    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(speech_recognition_result.text))
        return speech_recognition_result.text
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
        return None
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")
        return None
    
    #raise NotImplementedError
    

### Handle prompts entered by the user
def handle_prompt(chat_option, prompt):
    if chat_option == "On Your Data (AI Search)":
        handle_chat_prompt(prompt)
    elif chat_option == "Function Calls":
        handle_chat_prompt_with_functions(prompt)
    elif chat_option == "Assistants API":
        st.write("<h6 style='text-align: center; color: red;'>This feature is not yet implemented.</h5>", unsafe_allow_html=True)
    else:
        st.write("Please select a chat option before calling the chatbot.")

def option_changed():
    if "CurrentPage" in st.session_state: 
        del st.session_state["CurrentPage"]
        
def main():    
    st.write(
    """
    # Chat with Data

    This dashboard is intended to show off capabilities of Azure OpenAI, including integration with AI Search, Azure Speech Services, and external APIs.
    \n Use Case : Contoso Suites is a hotel chain that wants to provide a chatbot to its customers to help them find information about their stay.
    
    """
    )
    tooltip_text = """On Your Data Examples:  \nShow me all resorts with Swimming pool.   \n list all resorts in Bahamas  \n Which resorts with free parking, free breakfast and free gym.
      \n  \nFunction call examples:  \n List all customers in gold tier.  \n List customer with the name Hayden Cook.  \n List customers who stayed in hotel after August 2023.
    """

    chat_option = st.radio(label="Choose the chat option you want to try:", 
                           options=["On Your Data (AI Search)", "Function Calls", "Assistants API"], 
                           help=tooltip_text,
                           on_change=option_changed)

    if "CurrentPage" not in st.session_state or st.session_state["CurrentPage"] != "Chat with Data":        
        #first time on this page: Initialize session state variables        
        st.session_state["messages"] = []
        st.session_state["CurrentPage"] = "Chat with Data"

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 04: Await a speech to text request
    # Note that Streamlit does not have a great interface for keeping chat in a specific location
    # so using this button will cause it to be in an awkward position after the first message.
    
    ###########################################
    #Commenting....... - as this doesnt work on web app
    # if st.button("Speech to text"):
    #     speech_contents = recognize_from_microphone(speech_key, speech_region)
    #     if speech_contents:
    #         handle_prompt(chat_option, speech_contents)
    ############################################

    # Await a user message and handle the chat prompt when it comes in.
    if prompt := st.chat_input("Enter a message:"):
        handle_prompt(chat_option, prompt)

if __name__ == "__main__":
    main()
