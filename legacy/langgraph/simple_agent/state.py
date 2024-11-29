from typing import List, Optional
from pydantic import BaseModel

class GraphState(BaseModel):
    question: Optional[str] = None
    generation: Optional[str] = None
    documents: List[str] = []
