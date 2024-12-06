from fastapi import APIRouter, HTTPException, Body, Query
from fastapi.responses import StreamingResponse
from app.core.agents.langgraph.simple_agent.agent import LangSimpleRAG
from app.core.agents.langgraph.complex_agent.agent import LangComplexRAG
from app.core.config.schemas import AgentConfig
from app.core.config.default_config import DEFAULT_AGENT_CONFIG
from typing import Optional
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["Agents"])

@router.post(
    "/simple",
    summary="Query the simple RAG agent",
    description="""
    Sends a question to the simple RAG agent.
    
    - Can return a single response or stream updates
    - Can be configured with custom agent parameters
    - Returns retrieved documents and generated answer
    """,
    response_description="The agent's answer or a stream of updates"
)
async def simple_rag_agent(
    question: str = Body(..., embed=True, description="The question to ask the agent"),
    stream: bool = Body( 
        embed=True,
        default=False, 
        description="Whether to stream the response or return a single answer"
    ),
    config: Optional[AgentConfig] = Body(
        #default=None,
        description="Optional agent configuration. If not provided, uses default settings.",
        default={
            "llm": {
                "name": "gpt-4o-mini",
                "type": "openai",
                "parameters": {
                    "temperature": 0.7
                }
            },
            "retriever": {
                "collection_name": "default_collection",
                "search_type": "similarity",
                "k": 4,
                "search_parameters": {}
            },
            "agent_parameters": {}
        }
    )
):
    """Query the simple RAG agent with optional streaming and configuration"""
    try:
        # Initialize agent
        agent = LangSimpleRAG(config)
        
        if stream:
            def event_generator():
                try:
                    for output in agent.stream(question):
                        if isinstance(output, dict) and "error" in output:
                            yield f"data: {json.dumps({'error': output['error']})}\n\n"
                            break
                        yield f"data: {json.dumps(output)}\n\n"
                except Exception as e:
                    logger.error(f"Error in stream generation: {str(e)}")
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream"
            )
        else:
            result = agent.run(question)
            if isinstance(result, str) and result.startswith("Error:"):
                raise HTTPException(status_code=500, detail=result)
            return {"answer": result}
            
    except Exception as e:
        logger.error(f"Error in simple RAG agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/complex",
    summary="Query the complex RAG agent",
    description="""
    Sends a question to the complex RAG agent.
    
    - Can return a single response or stream updates
    - Can be configured with custom agent parameters
    - Supports multiple retrieval strategies and self-correction
    - Returns retrieved documents, feedback, and generated answer
    """,
    response_description="The agent's answer or a stream of updates"
)
async def complex_rag_agent(
    question: str = Body(..., embed=True, description="The question to ask the agent"),
    stream: bool = Body(
        embed=True,
        default=False, 
        description="Whether to stream the response or return a single answer"
    ),
    config: Optional[AgentConfig] = Body(
        #default=None,
        description="Optional agent configuration. If not provided, uses default settings.",
        default={
            "llm": {
                "name": "gpt-4o-mini",
                "type": "openai",
                "parameters": {
                    "temperature": 0.7
                }
            },
            "retriever": {
                "collection_name": "default_collection",
                "search_type": "similarity",
                "k": 4,
                "search_parameters": {}
            },
            "agent_parameters": {
                "max_retrievals": 3,
                "max_generations": 3,
            }
        }
    )
):
    """Query the complex RAG agent with optional streaming and configuration"""
    try:
        # Initialize agent
        agent = LangComplexRAG(config)
        
        if stream:
            def event_generator():
                try:
                    for output in agent.stream(question):
                        if isinstance(output, dict) and "error" in output:
                            yield f"data: {json.dumps({'error': output['error']})}\n\n"
                            break
                        yield f"data: {json.dumps(output)}\n\n"
                except Exception as e:
                    logger.error(f"Error in stream generation: {str(e)}")
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream"
            )
        else:
            result = agent.run(question)
            if isinstance(result, str) and result.startswith("Error:"):
                raise HTTPException(status_code=500, detail=result)
            return {"answer": result}
            
    except Exception as e:
        logger.error(f"Error in complex RAG agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))