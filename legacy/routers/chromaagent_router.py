from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from app.core.agents.langgraph.simple_agent.agent import SimpleRAGAgent
from app.core.agents.langgraph.complex_agent.agent import ComplexRAGAgent
from pydantic import BaseModel, Field
import json

router = APIRouter(prefix="/agent", tags=["Agent"])

@router.post(
    "/simple_rag/query",
    summary="Query the simple RAG agent",
    description="Sends a question to the RAG agent and receives a single response based on retrieved documents",
    response_description="The agent's answer to the question"
)
async def query_complex_rag_agent(
    question: str = Query(..., description="The question to ask the complex RAG agent")
):
    try:
        agent = SimpleRAGAgent()
        result = agent.run(question)
        if result.startswith("Error:"):
            raise HTTPException(status_code=500, detail=result)
        return {"answer": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/simple_rag/stream",
    summary="Stream responses from the simple RAG agent",
    description="Sends a question to the RAG agent and streams the response as it's being generated",
    response_description="Server-sent events stream of the agent's response"
)
async def stream_complex_rag_agent(
    question: str = Query(..., description="The question to ask the complex RAG agent")
):
    try:
        agent = SimpleRAGAgent()
        
        def event_generator():
            for output in agent.stream(question):
                if isinstance(output, dict) and "error" in output:
                    yield f"data: {json.dumps({'error': output['error']})}\n\n"
                    break
                yield f"data: {json.dumps(output)}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/complex_rag/query")
async def query_complex_rag_agent(
    question: str = Query(..., description="The question to ask the complex RAG agent")
):
    try:
        agent = ComplexRAGAgent()
        result = agent.run(question)
        if result.startswith("Error:"):
            raise HTTPException(status_code=500, detail=result)
        return {"answer": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/complex_rag/stream")
async def stream_complex_rag_agent(
    question: str = Query(..., description="The question to ask the complex RAG agent")
):
    try:
        agent = ComplexRAGAgent()
        
        def event_generator():
            for output in agent.stream(question):
                if isinstance(output, dict) and "error" in output:
                    yield f"data: {json.dumps({'error': output['error']})}\n\n"
                    break
                yield f"data: {json.dumps(output)}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))