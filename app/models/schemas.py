from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserInput(BaseModel):
    text: str
    session_id: Optional[int] = None
    
class RitualStep(BaseModel):
    step_number: int
    title: str
    content: str
    step_type: str
    
class Ritual(BaseModel):
    session_id: str
    user_state: str  # "anxious", "unfocused", "stressed", etc.
    steps: List[RitualStep]
    created_at: datetime = datetime.now()
    
class SessionMemory(BaseModel):
    session_id: str
    user_input: str
    user_state: str
    ritual_steps: List[str]
    rating: Optional[int] = None
    timestamp: datetime = datetime.now()
    
class RitualResponse(BaseModel):
    success: bool
    session_id: str
    ritual: Ritual
    message: str = "Ritual created successfully"
    
class FeedbackResponse(BaseModel):
    success: bool
    session_id: str
    rating: int
    message: str = "Feedback saved"
    