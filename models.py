from pydantic import BaseModel
from typing import List, Optional

# 1. What does an Email look like?
class Email(BaseModel):
    id: int
    sender: str
    subject: str
    body: str
    folder: str = "inbox" # Default folder

# 2. What can the AI DO? (The Request Payload)
class TriageAction(BaseModel):
    email_id: int
    target_folder: str  # e.g., "invoices", "support", "archived"

# 3. What does the AI SEE? (The Response Payload)
class TriageObservation(BaseModel):
    inbox_count: int
    emails: List[Email]
    message: str

# 4. How is the AI SCORED? (The Reward)
class TriageReward(BaseModel):
    score: float
    reason: str