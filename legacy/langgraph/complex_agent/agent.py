from .graph import rag_pipeline
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ComplexRAGAgent:
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
               