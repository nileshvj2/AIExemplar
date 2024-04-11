import os
import streamlit as st
import debugpy
import markdown
import requests
from dotenv import load_dotenv
from azure.cosmos import CosmosClient
import datetime

# if not debugpy.is_client_connected():
#     #debugpy.wait_for_client()
#     debugpy.listen(8501)  # Use a different port (e.g., 5679) if needed

os.chdir(os.path.dirname(os.path.abspath(__file__)))
st.set_page_config(layout="wide", page_title="AI Exemplar")

@st.cache_data
def get_access_token(CLIENT_ID: str, CLIENT_SECRET: str, request_token: str) -> str:
    """Obtain the request token from github.
    Given the client id, client secret and request issued out by GitHub, this method
    should give back an access token
    Parameters
    ----------
    CLIENT_ID: str
        A string representing the client id issued out by github
    CLIENT_SECRET: str
        A string representing the client secret issued out by github
    request_token: str
        A string representing the request token issued out by github
    Throws
    ------
    ValueError:
        if CLIENT_ID or CLIENT_SECRET or request_token is empty or not a string
    Returns
    -------
    access_token: str
        A string representing the access token issued out by github
    """
    if not CLIENT_ID:
        raise ValueError('The CLIENT_ID has to be supplied!')
    if not CLIENT_SECRET:
        raise ValueError('The CLIENT_SECRET has to be supplied!')
    if not request_token:
        raise ValueError('The request token has to be supplied!')
    if not isinstance(CLIENT_ID, str):
        raise ValueError('The CLIENT_ID has to be a string!')
    if not isinstance(CLIENT_SECRET, str):
        raise ValueError('The CLIENT_SECRET has to be a string!')
    if not isinstance(request_token, str):
        raise ValueError('The request token has to be a string!')

    url = f'https://github.com/login/oauth/access_token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&code={request_token}'
    headers = {
        'accept': 'application/json'
    }

    res = requests.post(url, headers=headers)

    data = res.json()
    access_token = None
    if 'access_token' in data:
        access_token = data['access_token']
    else:
        raise ValueError('The access token was not found in the response!')

    return access_token

@st.cache_data
def get_user_data(access_token: str) -> dict:
    """Obtain the user data from github.
    Given the access token issued out by GitHub, this method should give back the
    user data
    Parameters
    ----------
    request_token: str
        A string representing the request token issued out by github
    Throws
    ------
    ValueError:
        if access_token is empty or not a string
    Returns
    -------
    user_data: dict
        A dictionary with the users data:
        {
            "avatar_url": "https://avatars.githubusercontent.com/u/60782180?v=4",
            "bio": "Founder @oryksrobotics. I design and build robots for the logistics and supply chain industry.",
            "blog": "",
            "company": "oryks robotics",
            "created_at": "2020-02-07T12:49:50Z",
            "email": null,
            "events_url": "https://api.github.com/users/lyleokoth/events{/privacy}",
            "followers": 2,
            "followers_url": "https://api.github.com/users/lyleokoth/followers",
            "following": 8,
            "following_url": "https://api.github.com/users/lyleokoth/following{/other_user}",
            "gists_url": "https://api.github.com/users/lyleokoth/gists{/gist_id}",
            "gravatar_id": "",
            "hireable": null,
            "html_url": "https://github.com/lyleokoth",
            "id": 60782180,
            "location": "Nairobi, Kenya",
            "login": "lyleokoth",
            "name": null,
            "node_id": "MDQ6VXNlcjYwNzgyMTgw",
            "organizations_url": "https://api.github.com/users/lyleokoth/orgs",
            "public_gists": 0,
            "public_repos": 79,
            "received_events_url": "https://api.github.com/users/lyleokoth/received_events",
            "repos_url": "https://api.github.com/users/lyleokoth/repos",
            "site_admin": false,
            "starred_url": "https://api.github.com/users/lyleokoth/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/lyleokoth/subscriptions",
            "twitter_username": "lylethedesigner",
            "type": "User",
            "updated_at": "2022-03-21T11:00:43Z",
            "url": "https://api.github.com/users/lyleokoth"
        }
    """
    if not access_token:
        raise ValueError('The request token has to be supplied!')
    if not isinstance(access_token, str):
        raise ValueError('The request token has to be a string!')

    access_token = 'token ' + access_token
    url = 'https://api.github.com/user'
    headers = {"Authorization": access_token}

    resp = requests.get(url=url, headers=headers)

    userData = resp.json()

    return userData

def save_userlogin(cosmos_url, cosmos_key, cosmos_db, cosmos_container, user_data):
    client = CosmosClient(cosmos_url, credential=cosmos_key)
    database = client.get_database_client(cosmos_db)
    container = database.get_container_client(cosmos_container)
    container.create_item(user_data)

    
#streamlit run src\ContosoSuitesDashboard\Index.py 
def main():            
    #Load environment variables
    load_dotenv("credentials.env")
    GIT_CLIENT_ID = os.environ["GIT_CLIENT_ID"]
    GIT_CLIENT_SECRET = os.environ["GIT_CLIENT_SECRET"]
    GIT_SECRET_ACCESS_TOKEN = os.environ["GIT_SECRET_ACCESS_TOKEN"]
    AZURE_COSMOSDB_ENDPOINT = os.environ["AZURE_COSMOSDB_ENDPOINT"]
    AZURE_COSMOSDB_KEY = os.environ["AZURE_COSMOSDB_KEY"]
    AZURE_COSMOS_USER_CONTAINER = os.environ["AZURE_COSMOS_USER_CONTAINER"]
    AZURE_COSMOS_USER_DB = os.environ["AZURE_COSMOS_USER_DB"]
    SAVE_USER_LOGIN = os.environ["SAVE_USER_LOGIN"]
    show_login = False
    login_url=f"https://github.com/login/oauth/authorize?client_id={ GIT_CLIENT_ID }" 
    try:
      if("UserData" not in st.session_state and 'code' in st.query_params):          
          request_token = st.query_params['code']
          if request_token == GIT_SECRET_ACCESS_TOKEN:
            user_data = {"id": datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
                         "login": "Guest_Login", 
                         "name": "Guest User",
                         "email": "",
                          "location": "Guest Location",
                          "company": "Guest Company",
                          "login_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }            
          else: 
            access_token = get_access_token(GIT_CLIENT_ID, GIT_CLIENT_SECRET, request_token)
            user_data = get_user_data(access_token)
            user_data['login_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            user_data['id'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

          if(user_data is not None and 'login' in user_data):
              st.session_state["UserData"] = user_data
              save_userlogin(AZURE_COSMOSDB_ENDPOINT, AZURE_COSMOSDB_KEY, AZURE_COSMOS_USER_DB, AZURE_COSMOS_USER_CONTAINER, user_data) if SAVE_USER_LOGIN == 'True' else None

      if "UserData" in st.session_state:
          show_login = False
          user_data = st.session_state["UserData"] 
          welcome_string = "Welcome " + user_data['login'] 
          if user_data['name'] is not None:
            welcome_string += " (" + user_data['name'] + ")"  
          st.markdown("<h5 style='text-align: center; color: green;'>" + welcome_string + "</h5>", unsafe_allow_html=True)            


          #display readme file here...
          with open('README.md', 'r', encoding='utf-8') as f:
            markdown_string = f.read()
            # col1, col2, col3,col4 = st.columns(4)
            # with col2: 
            #     st.image("img/AIExemplar_chart.jpg", width=700)
            st.markdown(markdown_string, unsafe_allow_html=True)
      else:
          #raise ValueError('The user login not found!')
          show_login = True

    except Exception as e:
        show_login = False
        st.markdown("<h5 style='text-align: center; color: red;'>An error occurred while trying to login! </h5>", unsafe_allow_html=True)
        st.markdown("<h6 style='text-align: center; color: red;'>" + str(e) + "</h6>", unsafe_allow_html=True)        
    
    if show_login:
        st.markdown("<p style='text-align: center; color: red;'>Please <a href = " + login_url + "> login with Github </a> to access AI Exemplar! </p>", unsafe_allow_html=True)
        no_sidebar_style = """        
          <style>
              div[data-testid="stSidebarNav"] {display: none;}
          </style>
          """
        st.markdown(no_sidebar_style, unsafe_allow_html=True)
        
        

   

if __name__ == "__main__":
    main()
