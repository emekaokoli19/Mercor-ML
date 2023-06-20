import urllib.request, urllib.error, urllib.parse
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from nbformat import read
import tokenize
import io
import os
import openai
from dotenv import load_dotenv, dotenv_values
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import DeepLake
from repo import Repo
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import OpenAI

def get_chain():
    config = dotenv_values('.env')
    openai.api_key = config['OPENAI_API_KEY'] # insert your api key
    os.environ["ACTIVELOOP_TOKEN"] = config['ACTIVELOOP_TOKEN']
    os.environ['OPENAI_API_KEY'] = config['OPENAI_API_KEY']
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    # texts = text_splitter.split_text(code)
    # embeddings = OpenAIEmbeddings()
    # vectorstore = FAISS.from_texts(texts=texts, embedding=embeddings)
    # DEEPLAKE_ACCOUNT_NAME = "mekkyokoli"
    # db = DeepLake.from_texts(
    #     texts, embeddings, dataset_path=f"hub://{DEEPLAKE_ACCOUNT_NAME}/langchain-code"
    # )
    prompt_template: str = """You are a code analysis machine, given the following list of lists, where each list is 
    a list of strings and represent a code repository. Determine the 
    most technically complex and challenging repository, return the index of the most technically
    complex repository in the list and the justification of your selection with a short explanation. 
    Code:
    {code}

    Return the result in the following format: 
    index of repository: justification/explanation of selection
    """
    prompt = PromptTemplate(input_variables=["code"], template=prompt_template)
    llm = OpenAI(temperature=0.2)
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain
