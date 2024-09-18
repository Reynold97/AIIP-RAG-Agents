from pydantic import BaseModel
from typing import List, Literal, Optional

class GraphState(BaseModel):

    question: Optional[str] = None
    generation: Optional[str] = None
    documents: List[str] = []
    rewritten_question: Optional[str] = None
    query_feedbacks: List[str] = []
    generation_feedbacks: List[str] = []
    generation_num: int = 0
    retrieval_num: int = 0
    search_mode: Literal["vectorstore", "websearch", "QA_LM"] = "QA_LM"