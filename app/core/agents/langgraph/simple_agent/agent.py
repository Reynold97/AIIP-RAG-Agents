from typing import Optional
from langgraph.graph import StateGraph, START, END
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from app.core.indexers.chroma_indexer import ChromaIndexer
from app.core.config.schemas import AgentConfig, RetrieverConfig
from app.core.config.default_config import DEFAULT_AGENT_CONFIG
from .prompts import rag_prompt
from .state import GraphState
import logging

logger = logging.getLogger(__name__)

class LangSimpleRAG:
    """LangChain Graph-based Simple RAG Agent"""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize the agent with optional configuration"""
        self.config = config or DEFAULT_AGENT_CONFIG
        
        # Initialize all components
        self._initialize_components()
        self._initialize_chains()
        self._initialize_nodes()
        self.pipeline = self._build_pipeline()
    
    def _initialize_components(self):
        """Initialize base components: LLM and Retriever"""
        try:
            # Initialize LLM based on config
            self.llm = ChatOpenAI(
                model=self.config.llm.name,
                **self.config.llm.parameters
            )
            
            # Initialize Retriever with config
            self.indexer = ChromaIndexer(self.config.retriever)
            self.retriever = self.indexer.as_retriever()
            
            logger.info("Components initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing components: {str(e)}")
            raise
    
    def _initialize_chains(self):
        """Initialize all LangChain chains"""
        try:
            # Basic RAG chain with configured LLM
            self.rag_chain = rag_prompt | self.llm | StrOutputParser()
            
            logger.info("Chains initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing chains: {str(e)}")
            raise
            
    def _initialize_nodes(self):
        """Initialize graph nodes"""
        try:
            # Retrieval node function
            def retriever_node(state: GraphState):
                new_documents = self.retriever.invoke(state.question)
                new_documents = [d.page_content for d in new_documents]
                state.documents.extend(new_documents)
                return {"documents": state.documents}
            
            # Generation node function
            def generation_node(state: GraphState):
                generation = self.rag_chain.invoke({
                    "context": "\n\n".join(state.documents), 
                    "question": state.question, 
                })
                return {"generation": generation}
            
            # Store nodes for pipeline building
            self.retriever_node = retriever_node
            self.generation_node = generation_node
            
            logger.info("Nodes initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing nodes: {str(e)}")
            raise
    
    def _build_pipeline(self) -> StateGraph:
        """Build the LangGraph pipeline"""
        try:
            # Create graph
            graph = StateGraph(GraphState)
            
            # Add nodes
            graph.add_node('retrieval_node', self.retriever_node)
            graph.add_node('generator_node', self.generation_node)
            
            # Connect nodes
            graph.add_edge(START, 'retrieval_node')
            graph.add_edge('retrieval_node', 'generator_node')
            graph.add_edge('generator_node', END)
            
            logger.info("Pipeline built successfully")
            return graph.compile()
            
        except Exception as e:
            logger.error(f"Error building pipeline: {str(e)}")
            raise

    def run(self, question: str) -> str:
        """Run the agent synchronously
        
        Args:
            question: The question to answer
            
        Returns:
            str: Generated answer
            
        Raises:
            Exception: If any error occurs during execution
        """
        try:
            inputs = {"question": question}
            result = self.pipeline.invoke(inputs)
            return result["generation"]
        except Exception as e:
            logger.error(f"Error running agent: {str(e)}")
            raise

    def stream(self, question: str):
        """Stream the agent's response
        
        Args:
            question: The question to answer
            
        Yields:
            dict: Stream of updates from the pipeline
            
        Raises:
            Exception: If any error occurs during execution
        """
        try:
            inputs = {"question": question}
            for output in self.pipeline.stream(inputs, stream_mode='updates'):
                yield output
        except Exception as e:
            logger.error(f"Error streaming response: {str(e)}")
            raise