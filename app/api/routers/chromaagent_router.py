from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from app.core.agents.langgraph.simple_agent import create_chroma_simple_rag_agent
from app.core.agents.langgraph.complex_agent.agent import ComplexRAGAgent
import json
import logging

router = APIRouter(prefix="/agent", tags=["Agent"])

@router.post("/simple_rag/{collection_name}/query")
async def query_simple_rag_agent(
    collection_name: str,
    k: int = 4,
    question: str = Query(..., description="The question to ask the RAG agent")
):
    try:
        agent = create_chroma_simple_rag_agent(collection_name, k)
        result = agent.run(question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simple_rag/{collection_name}/stream")
async def stream_simple_rag_agent(
    collection_name: str,
    k: int = 4,
    question: str = Query(..., description="The question to ask the RAG agent")
):
    try:
        agent = create_chroma_simple_rag_agent(collection_name, k)
        
        def event_generator():
            for output in agent.stream(question):
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