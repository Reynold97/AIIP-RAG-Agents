import os
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv

load_dotenv()

os.environ['TAVILY_API_KEY'] = 'YOUR API KEY'

web_search_tool = TavilySearchResults(k=3)