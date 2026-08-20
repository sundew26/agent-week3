from pydantic import BaseModel


class StartRequest(BaseModel):
    question: str


class ReviewRequest(BaseModel):
    workflow_id: str
    status: str  # "approved" | "rejected"
    feedback: str = ""
