from app.core.indexers.chroma_indexer import ChromaIndexer
from .chains import rag_chain
from .state import GraphState 

indexer = ChromaIndexer("default_collection")
retriever = indexer.as_retriever()

def retriever_node(state: GraphState):
    new_documents = retriever.invoke(state.question)
    new_documents = [d.page_content for d in new_documents]
    state.documents.extend(new_documents)
    return {"documents": state.documents}

def generation_node(state: GraphState):
    generation = rag_chain.invoke({
        "context": "\n\n".join(state.documents), 
        "question": state.question, 
    })
    return {"generation": generation}