import os
import streamlit as st
import debugpy
import markdown
import requests
from dotenv import load_dotenv

def logout():
    #Delete all the items in Session state
    for key in st.session_state.keys():
        del st.session_state[key]

def main():            
    logout()
    st.switch_page("Index.py")
    

if __name__ == "__main__":
    main()