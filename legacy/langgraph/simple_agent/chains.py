from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from .graph import GraphState
from .prompts import rag_prompt

llm_engine = ChatOpenAI(model='gpt-4o-mini')

#Chains
rag_chain = rag_prompt | llm_engine | StrOutputParser()