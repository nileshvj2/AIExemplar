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


def generate_contents(code_text):
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

    
    message_text = [{"role":"system","content":"""
                    You are an AI assistant that interprets the given code snippet and generates documentation for the code.
                    Use below code snippet to generate documentation for the code in natural language Make sure documentation is in concise and clear format.   
                    Please see below code.
                    
                    """ + code_text 
                    }
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
    # Code Narrator! 
    Use case: Generate documentation for given code snippet.     
    """
    )

    user_input  = st.text_area("Paste your code here: ", key="question", height=250, value = '''{
                               using System;
    using System.IO;
    using Excel = Microsoft.Office.Interop.Excel;

    // ...

    FileInfo fileInfo;
    Excel.Application excelApp = new Excel.Application();
    excelApp.Visible = false;

    if (listView1.Items.Count > 0)
    {
        foreach (ListViewItem item in listView1.Items)
        {
            fileInfo = new FileInfo(item.Text);
            if (fileInfo.Extension == ".xls" || fileInfo.Extension == ".xlsx" || fileInfo.Extension == ".xlt" || fileInfo.Extension == ".xlsm" || fileInfo.Extension == ".csv")
            {
                Excel.Workbook workbook = excelApp.Workbooks.Open(item.Text, 0, true, 5, "", "", true, Excel.XlPlatform.xlWindows, "\t", false, false, 0, true, false, false);
                for (int count = 1; count <= workbook.Sheets.Count; count++)
                {
                    Excel.Worksheet worksheet = (Excel.Worksheet)workbook.Worksheets.get_Item(count);
                    worksheet.Activate();
                    worksheet.Visible = false;
                    worksheet.UsedRange.Cells.Select();
                    // Process data from the worksheet as needed
                }
            }
        }
    }


    ''')    

    resp = ""    
    
    if st.button("Generate Documentation"):            
        resp = generate_contents(user_input)
        st.markdown("Here is the generated documentation for the code snippet:   \n  \n" + resp, unsafe_allow_html=True)
        st.session_state.messages.append("Product description generated successfully!")
    
    

if __name__ == "__main__":
    main()

