from langgraph.graph import StateGraph, START, END
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnableSequence
from .state import GraphState
from .nodes import create_retriever_node, create_generation_node

def build_rag_pipeline(retriever: BaseRetriever, generation_chain: RunnableSequence):
    pipeline = StateGraph(GraphState)
    
    # Create nodes
    retriever_node = create_retriever_node(retriever)
    generator_node = create_generation_node(generation_chain)
    
    # Add nodes
    pipeline.add_node('retrieval_node', retriever_node)
    pipeline.add_node('generator_node', generator_node)
    
    # Connect nodes
    pipeline.add_edge(START, 'retrieval_node')
    pipeline.add_edge('retrieval_node', 'generator_node')
    pipeline.add_edge('generator_node', END)
    
    return pipeline.compile()