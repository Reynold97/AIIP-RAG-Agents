from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnableSequence
from app.core.indexers.chroma_indexer import ChromaIndexer
from .chains import rag_chain
from .state import GraphState

def create_retriever_node(retriever: BaseRetriever):
    def retriever_node(state: GraphState):
        new_documents = retriever.invoke(state.question)
        new_documents = [d.page_content for d in new_documents]
        state.documents.extend(new_documents)
        return {"documents": state.documents}
    return retriever_node

def create_generation_node(generation_chain: RunnableSequence):
    def generation_node(state: GraphState):
        generation = generation_chain.invoke({
            "context": "\n\n".join(state.documents), 
            "question": state.question, 
        })
        return {"generation": generation}
    return generation_node