from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnableSequence
from .graph import build_rag_pipeline
from .state import GraphState

class SimpleRAGAgent:
    def __init__(self, retriever: BaseRetriever, generation_chain: RunnableSequence, max_retrievals: int = 4):
        self.retriever = retriever
        self.generation_chain = generation_chain
        self.pipeline = build_rag_pipeline(self.retriever, self.generation_chain)

    def run(self, question: str):
        inputs = {"question": question}
        result = self.pipeline.invoke(inputs)
        return result["generation"]

    def stream(self, question: str):
        inputs = {"question": question}
        for output in self.pipeline.stream(inputs, stream_mode='updates'):
            yield output
               
            