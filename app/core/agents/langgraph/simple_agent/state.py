from typing import List, Optional
from pydantic import BaseModel

class GraphState(BaseModel):
    #Graph Parameterss
    question: Optional[str] = None
    generation: Optional[str] = None
    documents: List[str] = []
