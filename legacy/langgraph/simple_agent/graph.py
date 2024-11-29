from langgraph.graph import StateGraph, START, END
from .state import GraphState
from .nodes import retriever_node, generation_node

# Create the pipeline
pipeline = StateGraph(GraphState)
    
# Add nodes
pipeline.add_node('retrieval_node', retriever_node)
pipeline.add_node('generator_node', generation_node)
    
# Connect nodes
pipeline.add_edge(START, 'retrieval_node')
pipeline.add_edge('retrieval_node', 'generator_node')
pipeline.add_edge('generator_node', END)

# Compile pipeline
rag_pipeline = pipeline.compile()