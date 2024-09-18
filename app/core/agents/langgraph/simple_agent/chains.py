from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from .prompts import rag_prompt

load_dotenv()

llm_engine = ChatOpenAI(model='gpt-4o-mini')  
rag_chain = rag_prompt | llm_engine | StrOutputParser()