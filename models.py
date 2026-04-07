from pydantic import BaseModel
from typing import List, Optional
class Email(BaseModel):
    id: int
    sender: str
    subject: str
    body: str
    folder: str = "inbox"           # where the email currently is
    correct_folder: str = "inbox"   
    category: str = "unknown"       # person readable label: "billing", "complaint", etc.
class TriageAction(BaseModel):
    email_id: int
    target_folder: str
class TriageObservation(BaseModel):
    inbox_count: int
    emails: List[Email]
    message: str
class TriageReward(BaseModel):
    score: float
    reason: str