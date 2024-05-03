# AI Exemplar 

This project serves as a collection of proof-of-concept for Azure OpenAI and other AI functionalities within Azure. It demonstrates various use cases, design patterns, and implementation options. The goal is to provide a foundation for architects and AI enthusiast to explore the potential of Azure AI and make informed decisions about solution approaches. 
The site map (chart) illustrates various use cases, including Q&A over enterprise data, classification, and call center applications etc. These use cases leverage diverse data sources such as SQL DB, Cosmos DB, PDF files, CSV files, and Delta Lake etc. The primary goal of this project is not only to showcase different use cases but also to explore various implementation options. By considering different approaches, the architects and AI enthusiast can gain insights into the pros, cons, and complexities associated with each solution. For instance, comparing techniques like Lang chain versus Semantic Kernel or choosing between building Q&A systems over Delta Lake using SQL endpoint versus Vector search methods and many more scenarios.

Use the navigation bar on the left to navigate to the different option pages And then choose radio buttons to choose subcategory.

![AI Exemplar Solution Chart](https://github.com/nileshvj2/AI_Exemplar2/blob/main/img/AIExemplar_chart.jpg)

### Solutions Catalog:

* ##### <span style="color:lightblue"> Chat with Data </span>:
  Sample Chat with Data features using different data sources.

  a) On Your Data (AI Search) b) Function calling c) Assistants API

* ##### <span style="color:lightblue"> Chat with DB </span> :
  POC for structured data like SQL DB and NoSQL like Cosmos DB.

  a) QA Over SQL DB b) QA Over Cosmos DB

* ##### <span style="color:lightblue"> Chat with CSV </span>:
  POC showing how natural language interface can be built on any csv file using LLM and Agents.

* ##### <span style="color:lightblue"> Chat with DeltaLake </span> :
  This option shows how Chat interface can be built on structured data sources like Delta Lake.

  a) QA Over Delta lake (SQL) b) QA Over Delta lake (Vector)

* ##### <span style="color:lightblue"> Chat with Multiple Datasources </span> :
  This POC shows various implementation patterns for building chat interface on multiple data sources using Azure AI services and Orchestrators.

  a) Langchain b) Semantic Kernel

* ##### <span style="color:lightblue"> Call Center Analytics </span>:
  This is illustration of how Azure AI services like Speech to text, Summarization, sentiment analysis etc. along with Open AI models used in popular call center use case.

  a) Speech to Text and Transcription b) Live call recording transcription c) Summarization d) Sentiment Analysis e) Entity Extraction

* ##### <span style="color:lightblue"> Classification </span>:<span style="color:red;font-size: small"> Coming Soon! </span>
  This is example of how Large Language Models like GPT-4 can be used for classification scenarios.

  a) Embeddings b) Fine Tuning

* ##### <span style="color:lightblue"> Unstructured to Structured data </span>:<span style="color:red;font-size: small"> Coming Soon! </span>
  This option is proof of concept for scenarios where conversion from unstructured data to structured data is required. This can be used as demonstration of how LLM can be used to get meaningful insights from unstructured data and integrate with App/Structured databases.

* ##### <span style="color:lightblue"> Content Generation </span>:
  This is sample of how LLM can be used for content generation use cases.

* ##### <span style="color:lightblue"> HR Recruitment </span>: <span style="color:red;font-size: small"> Coming Soon! </span>
  This is sample of how LLM can be used for HR recruitment use cases to short list candidates based on job description and resume.

* ##### <span style="color:lightblue"> Code Narrator </span>:
  This example provides LLM capabilities to generate code documentation from code snippets in common programming languages.


### Disclaimer
The information and code contained in this repo and any accompanying materials (including, but not limited to, scripts, sample codes, etc.) are provided “AS-IS” and “WITH ALL FAULTS.” by owner and contributors of the repo. 
Code and information in this repo is provided solely for demonstration purposes and does not represent Microsoft or any other company's official documentation. Author assumes no liability arising from your use of this material.
