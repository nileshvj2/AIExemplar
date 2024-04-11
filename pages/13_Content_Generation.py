import streamlit as st
import requests
import pandas as pd
import json
import openai
import inspect
import azure.cognitiveservices.speech as speechsdk
import pyodbc
from openai import AzureOpenAI
import pandas as pd
import os
from dotenv import load_dotenv

st.set_page_config(layout="wide")

# Load environment variables
load_dotenv("credentials.env")

aoai_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
aoai_api_key = os.environ["AZURE_OPENAI_API_KEY"]
deployment_name = os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]
aoai_api_version = os.environ["AZURE_OPENAI_API_VERSION"] #"2023-05-15"
aoai_api_type = os.environ["AZURE_OPENAI_API_TYPE"]


def generate_contents(json_data, type):
    """
    Generate code documentation for the given code snippet.
    """
    st.session_state.messages = []
    st.session_state.messages.append("Generating Contents...")
    #st.experimental_rerun()
    code = st.session_state.question
    client = AzureOpenAI(
        api_key=aoai_api_key,  
        api_version=aoai_api_version,
        azure_endpoint = aoai_endpoint
        )

    if(type == "description"):
        message_text = [{"role":"system","content":"""
                        You are an AI assistant that generates description of a products from given json data. 
                        You can use product name, brand name, category name, model year, list price fields in order to generate description of the product in natural language.
                        return the description of the product in the following format:
                        {
                            "id": "12345",
                            "title": "Mountain Climber by Trek",
                            "content": "Explore the great outdoors with the 2016 Trek Mountain Climber. This rugged mountain bike, categorized under Mountain Bikes, is designed to handle the toughest terrains with ease. With its durable build and responsive handling, you'll conquer steep hills and rocky paths confidently. The model year 2016 ensures you're riding on tried and tested technology, while the list price of $850.00 represents excellent value for a bike of this caliber. Experience the adventure with Trek's commitment to quality and performance."
                        }
                        Here is json data for a product:
                        
                        """ + json.dumps(json_data, indent=4) }
                    ]
    else:
        message_text = [{"role":"system","content":"""
                You are an AI assistant that generates advertisements for the products from given json data. 
                You can use product name, brand name, category name, model year, list price fields to generate advertisement of the product in natural language.
                return the advertisement in text format and less than 800 characters.
                Here is json data for a product:
                
                """ + json.dumps(json_data, indent=4) }
            ]
    
    completion = client.chat.completions.create(
        model= deployment_name,
        messages = message_text,
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    resp = completion.choices[0].message.content
    #st.session_state["output"] = resp
    #st.write(resp)
    st.session_state.messages.append("Code documentation generated successfully!")    

    return completion.choices[0].message.content

    

def main():
    st.session_state.messages = []
    st.write(
    """
    # Content Generator! 
    Use case: Generate Product description and advertisement from product structured data. 
    Provide Json formatted product data which should have attributes like id, product_name and other related fields.
    Using LLM's content generation capabilities, new product description or advertisement text will be generated. Product description will be in json format so that it can be integrated with other applications. 
    """
    )

    user_input  = st.text_area("Add your product json data here: ", key="question", height=250, value = '''{
        "id": 321,
        "product_name": "Trek Checkpoint ALR Frameset - 2019",
        "brand_id": 9,
        "brand_name": "Trek",
        "category_id": 7,
        "category_name": "Road Bikes",
        "model_year": 2019,
        "list_price": 2999.99
    }''')    

    resp = ""
    col1, col2, col3, col4, col5  = st.columns(5) 
    with col1:        
        if st.button("Create Product Description"):            
            resp = generate_contents(user_input, type = "description")
            #st.markdown("Here is the generated product description:  \n  \n" + resp, unsafe_allow_html=True)
            st.session_state.messages.append("Product description generated successfully!")
    with col2:
        if st.button("Create Advertisement"):
            resp = generate_contents(user_input, type = "advertisement")
            st.session_state.messages.append("Product Advertisement created successfully!")
    
    output_content = st.text_area("Generated Output: ", key="output", height=250, disabled=True, value= resp)



if __name__ == "__main__":
    main()

