from typing import Optional, List, Dict, Any
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from app.core.indexers.chroma_indexer import ChromaIndexer
from app.core.config.schemas import AgentConfig
from app.core.config.default_config import DEFAULT_AGENT_CONFIG
from langchain_core.output_parsers import StrOutputParser
from .state import GraphState
from .tools import web_search_tool
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class LangComplexRAG:
    """LangChain Graph-based Complex RAG Agent with multiple feedback loops"""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize the agent with optional configuration"""
        self.config = config or DEFAULT_AGENT_CONFIG
        
        # Get agent-specific parameters with defaults
        self.MAX_RETRIEVALS = self.config.agent_parameters.get("max_retrievals", 3)
        self.MAX_GENERATIONS = self.config.agent_parameters.get("max_generations", 3)
        
        logger.info(f"Initializing LangComplexRAG with max_retrievals={self.MAX_RETRIEVALS}, "
                   f"max_generations={self.MAX_GENERATIONS}")
        
        # Initialize all components
        self._initialize_components()
        self._initialize_output_parsers()
        self._initialize_chains()
        self._initialize_nodes()
        self.pipeline = self._build_pipeline()
    
    def run(self, question: str) -> str:
        """Run the agent synchronously"""
        try:
            recursion_limit = self.config.agent_parameters.get("recursion_limit", 50)
            inputs = ({"question": question}, {"recursion_limit": recursion_limit})
            result = self.pipeline.invoke(inputs)
            return result["generation"]
        except Exception as e:
            logger.error(f"Error running agent: {str(e)}")
            raise

    def stream(self, question: str):
        """Stream the agent's response"""
        try:
            recursion_limit = self.config.agent_parameters.get("recursion_limit", 50)
            inputs = ({"question": question}, {"recursion_limit": recursion_limit})
            for output in self.pipeline.stream(inputs, stream_mode='updates'):
                yield output
        except Exception as e:
            logger.error(f"Error streaming response: {str(e)}")
            raise
        
    def _initialize_components(self):
        """Initialize base components: LLM and Retriever"""
        try:
            # Initialize LLM
            self.llm_engine = ChatOpenAI(
                model=self.config.llm.name,
                **self.config.llm.parameters
            )
            
            # Initialize Retriever
            self.indexer = ChromaIndexer(self.config.retriever)
            self.retriever = self.indexer.as_retriever()
            
            logger.info("Components initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing components: {str(e)}")
            raise
            
    def _initialize_output_parsers(self):
        """Initialize Pydantic output parsers for structured outputs"""
        try:
            from .utils import (
                GradeHallucinations,
                GradeDocuments,
                GradeAnswer,
                RouteQuery
            )
            
            # Store parser classes
            self.parsers = {
                "hallucination": GradeHallucinations,
                "documents": GradeDocuments,
                "answer": GradeAnswer,
                "route": RouteQuery
            }
            
            logger.info("Output parsers initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing output parsers: {str(e)}")
            raise
    
    def _initialize_chains(self):
        """Initialize all LangChain chains"""
        try:
            from .prompts import (
                rag_prompt,
                db_query_rewrite_prompt,
                hallucination_prompt,
                answer_prompt,
                query_feedback_prompt,
                generation_feedback_prompt,
                give_up_prompt,
                grade_doc_prompt,
                knowledge_extraction_prompt,
                router_prompt,
                websearch_query_rewrite_prompt,
                simple_question_prompt
            )
            
            # Basic chains
            self.rag_chain = rag_prompt | self.llm_engine | StrOutputParser()
            self.db_query_rewriter = db_query_rewrite_prompt | self.llm_engine | StrOutputParser()
            self.query_feedback_chain = query_feedback_prompt | self.llm_engine | StrOutputParser()
            self.generation_feedback_chain = generation_feedback_prompt | self.llm_engine | StrOutputParser()
            self.give_up_chain = give_up_prompt | self.llm_engine | StrOutputParser()
            self.knowledge_extractor = knowledge_extraction_prompt | self.llm_engine | StrOutputParser()
            self.websearch_query_rewriter = websearch_query_rewrite_prompt | self.llm_engine | StrOutputParser()
            self.simple_question_chain = simple_question_prompt | self.llm_engine | StrOutputParser()
            
            # Structured output chains
            self.hallucination_grader = hallucination_prompt | self.llm_engine.with_structured_output(self.parsers["hallucination"])
            self.answer_grader = answer_prompt | self.llm_engine.with_structured_output(self.parsers["answer"])
            self.retrieval_grader = grade_doc_prompt | self.llm_engine.with_structured_output(self.parsers["documents"])
            self.question_router = router_prompt | self.llm_engine.with_structured_output(self.parsers["route"])
            
            logger.info("Chains initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing chains: {str(e)}")
            raise
    
    def _initialize_nodes(self):
        """Initialize all nodes with exact same logic as original"""
        try:
            def retriever_node(state: GraphState):
                new_documents = self.retriever.invoke(state.rewritten_question)
                new_documents = [d.page_content for d in new_documents]
                state.documents.extend(new_documents)
                return {
                    "documents": state.documents, 
                    "retrieval_num": state.retrieval_num + 1
                }

            def generation_node(state: GraphState):
                generation = self.rag_chain.invoke({
                    "context": "\n\n".join(state.documents), 
                    "question": state.question, 
                    "feedback": "\n".join(state.generation_feedbacks)
                })
                return {
                    "generation": generation,
                    "generation_num": state.generation_num + 1
                }

            def db_query_rewriting_node(state: GraphState):
                rewritten_question = self.db_query_rewriter.invoke({
                    "question": state.question,
                    "feedback": "\n".join(state.query_feedbacks)
                })
                return {"rewritten_question": rewritten_question, "search_mode": "vectorstore"} 

            def answer_evaluation_node(state: GraphState):
                # assess hallucination
                hallucination_grade = self.hallucination_grader.invoke(
                    {"documents": state.documents, "generation": state.generation}
                )
                if hallucination_grade.binary_score == "yes":
                    # if no hallucination, assess relevance
                    answer_grade = self.answer_grader.invoke({
                        "question": state.question, 
                        "generation": state.generation
                    })
                    if answer_grade.binary_score == "yes":
                        # no hallucination and relevant
                        return "useful"
                    elif state.generation_num > self.MAX_GENERATIONS:
                        return "max_generation_reached"
                    else:
                        # no hallucination but not relevant
                        return "not relevant"
                elif state.generation_num > self.MAX_GENERATIONS:
                    return "max_generation_reached"
                else:
                    # we have hallucination
                    return "hallucination" 
                
            def generation_feedback_node(state: GraphState):
                feedback = self.generation_feedback_chain.invoke({
                    "question": state.question,
                    "documents": "\n\n".join(state.documents),
                    "generation": state.generation
                })

                feedback = 'Feedback about the answer "{}": {}'.format(
                    state.generation, feedback
                )
                state.generation_feedbacks.append(feedback)
                return {"generation_feedbacks": state.generation_feedbacks}

            def query_feedback_node(state: GraphState):
                feedback = self.query_feedback_chain.invoke({
                    "question": state.question,
                    "rewritten_question": state.rewritten_question,
                    "documents": "\n\n".join(state.documents),
                    "generation": state.generation
                })

                feedback = 'Feedback about the query "{}": {}'.format(
                    state.rewritten_question, feedback
                )
                state.query_feedbacks.append(feedback)
                return {"query_feedbacks": state.query_feedbacks}

            def give_up_node(state: GraphState):
                response = self.give_up_chain.invoke(state.question)
                return {"generation": response}

            def filter_relevant_documents_node(state: GraphState):
                # first, we grade every documents
                grades = self.retrieval_grader.batch([
                    {"question": state.question, "document": doc} 
                    for doc in state.documents
                ])
                # Then we keep only the documents that were graded as relevant
                filtered_docs = [
                    doc for grade, doc 
                    in zip(grades, state.documents) 
                    if grade.binary_score == 'yes'
                ]

                # If we didn't get any relevant document, let's capture that 
                # as a feedback for the next retrieval iteration
                if not filtered_docs:
                    feedback = 'Feedback about the query "{}": did not generate any relevant documents.'.format(
                        state.rewritten_question
                    )
                    state.query_feedbacks.append(feedback)

                return {
                    "documents": filtered_docs, 
                    "query_feedbacks": state.query_feedbacks
                }

            def knowledge_extractor_node(state: GraphState):
                filtered_docs = self.knowledge_extractor.batch([
                    {"question": state.question, "document": doc} 
                    for doc in state.documents
                ])
                # we keep only the non empty documents
                filtered_docs = [doc for doc in filtered_docs if doc]
                return {"documents": filtered_docs}

            def router_node(state: GraphState):
                route_query = self.question_router.invoke(state.question)
                return route_query.route

            def simple_question_node(state: GraphState):
                answer = self.simple_question_chain.invoke(state.question)
                return {"generation": answer, "search_mode": "QA_LM"}

            def websearch_query_rewriting_node(state: GraphState):
                rewritten_question = self.websearch_query_rewriter.invoke({
                    "question": state.question, 
                    "feedback": "\n".join(state.query_feedbacks)
                })
                if state.search_mode != "websearch":
                    state.retrieval_num = 0    
                return {
                    "rewritten_question": rewritten_question, 
                    "search_mode": "websearch",
                    "retrieval_num": state.retrieval_num
                }

            def web_search_node(state: GraphState):
                try:
                    new_docs = web_search_tool.invoke(
                        {"query": state.rewritten_question}
                    )
                    
                    if isinstance(new_docs, str):
                        web_results = [new_docs]
                    elif isinstance(new_docs, list):
                        web_results = [d.get("content", str(d)) if isinstance(d, dict) else str(d) for d in new_docs]
                    else:
                        web_results = [str(new_docs)]
                    
                    state.documents.extend(web_results)
                    return {
                        "documents": state.documents, 
                        "retrieval_num": state.retrieval_num + 1
                    }
                except Exception as e:
                    return {
                        "error": f"Web search failed: {str(e)}",
                        "retrieval_num": state.retrieval_num + 1
                    }

            def search_mode_node(state: GraphState):
                return state.search_mode

            def relevant_documents_validation_node(state: GraphState):
                if state.documents:
                    # we have relevant documents
                    return "knowledge_extraction"
                elif state.search_mode == 'vectorsearch' and state.retrieval_num > self.MAX_RETRIEVALS:
                    # we don't have relevant documents
                    # and we reached the maximum number of retrievals
                    return "max_db_search"
                elif state.search_mode == 'websearch' and state.retrieval_num > self.MAX_RETRIEVALS:
                    # we don't have relevant documents
                    # and we reached the maximum number of websearches
                    return "max_websearch"
                else:
                    # we don't have relevant documents
                    # so we retry the search
                    return state.search_mode

            self.nodes = {
                "retriever_node": retriever_node,
                "generation_node": generation_node,
                "db_query_rewriting_node": db_query_rewriting_node,
                "generation_feedback": generation_feedback_node,
                "generation_feedback_node": query_feedback_node,
                "give_up_node": give_up_node,
                "filter_relevant_documents_node": filter_relevant_documents_node,
                "knowledge_extractor_node": knowledge_extractor_node,
                "simple_question_node": simple_question_node,
                "websearch_query_rewriting_node": websearch_query_rewriting_node,
                "web_search_node": web_search_node,
                "router_node": router_node,
                "search_mode_node": search_mode_node,
                "answer_evaluation_node": answer_evaluation_node,
                "relevant_documents_validation_node": relevant_documents_validation_node
            }
            
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
            graph.add_node('db_query_rewrite_node', self.nodes['db_query_rewriting_node'])
            graph.add_node('retrieval_node', self.nodes['retriever_node'])
            graph.add_node('generator_node', self.nodes['generation_node'])
            graph.add_node('query_feedback_node', self.nodes['generation_feedback_node'])  # Note the name change here
            graph.add_node('generation_feedback_node', self.nodes['generation_feedback'])  # And here
            graph.add_node('simple_question_node', self.nodes['simple_question_node'])
            graph.add_node('websearch_query_rewriting_node', self.nodes['websearch_query_rewriting_node'])
            graph.add_node('web_search_node', self.nodes['web_search_node'])
            graph.add_node('give_up_node', self.nodes['give_up_node'])
            graph.add_node('filter_docs_node', self.nodes['filter_relevant_documents_node'])
            graph.add_node('extract_knowledge_node', self.nodes['knowledge_extractor_node'])

            # Add conditional edges from START
            graph.add_conditional_edges(
                START,
                self.nodes['router_node'],
                {
                    "vectorstore": 'db_query_rewrite_node',
                    "websearch": 'websearch_query_rewriting_node',
                    "QA_LM": 'simple_question_node'
                }
            )

            # Add simple edges
            graph.add_edge('db_query_rewrite_node', 'retrieval_node')
            graph.add_edge('retrieval_node', 'filter_docs_node')
            graph.add_edge('extract_knowledge_node', 'generator_node')
            graph.add_edge('websearch_query_rewriting_node', 'web_search_node')
            graph.add_edge('web_search_node', 'filter_docs_node')
            graph.add_edge('generation_feedback_node', 'generator_node')
            graph.add_edge('simple_question_node', END)
            graph.add_edge('give_up_node', END)

            # Add conditional edges for answer evaluation
            graph.add_conditional_edges(
                'generator_node',
                self.nodes['answer_evaluation_node'],
                {
                    "useful": END,
                    "not relevant": 'query_feedback_node',
                    "hallucination": 'generation_feedback_node',
                    "max_generation_reached": 'give_up_node'
                }
            )

            # Add conditional edges for search mode
            graph.add_conditional_edges(
                'query_feedback_node',
                self.nodes['search_mode_node'],
                {
                    "vectorstore": 'db_query_rewrite_node',
                    "websearch": 'websearch_query_rewriting_node',
                }
            )

            # Add conditional edges for document validation
            graph.add_conditional_edges(
                'filter_docs_node',
                self.nodes['relevant_documents_validation_node'],
                {
                    "knowledge_extraction": 'extract_knowledge_node',
                    "websearch": 'websearch_query_rewriting_node',
                    "vectorstore": 'db_query_rewrite_node',
                    "max_db_search": 'websearch_query_rewriting_node',
                    "max_websearch": 'give_up_node'
                }
            )

            logger.info("Pipeline built successfully")
            return graph.compile()

        except Exception as e:
            logger.error(f"Error building pipeline: {str(e)}")
            raise