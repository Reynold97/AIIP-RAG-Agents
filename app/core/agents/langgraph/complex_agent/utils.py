from typing import Literal
from pydantic import BaseModel, Field

class GradeHallucinations(BaseModel):
    binary_score: Literal["yes", "no"] = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )

class GradeDocuments(BaseModel):
    binary_score: Literal["yes", "no"] = Field(
        description="Document is relevant to the question, 'yes' or 'no'"
    )

class GradeAnswer(BaseModel):
    binary_score: Literal["yes", "no"] = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )

class RouteQuery(BaseModel):
    route: Literal["vectorstore", "websearch", "QA_LM"] = Field(
        description="Given a user question choose to route it to web search (websearch), a vectorstore (vectorstore), or a QA language model (QA_LM).",
    )