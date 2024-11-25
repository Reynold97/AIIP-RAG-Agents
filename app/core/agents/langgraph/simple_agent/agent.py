from .graph import rag_pipeline

class SimpleRAGAgent:
    def __init__(self):
        self.pipeline = rag_pipeline

    def run(self, question: str):
        inputs = {"question": question}
        result = self.pipeline.invoke(inputs)
        return result["generation"]

    def stream(self, question: str):
        inputs = {"question": question}
        for output in self.pipeline.stream(inputs, stream_mode='updates'):
            yield output
               
            