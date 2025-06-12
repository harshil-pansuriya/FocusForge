from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Schema for user input data
class UserInput(BaseModel):
    text: str
    session_id: Optional[str] = None
    
# Schema for individual ritual step
class RitualStep(BaseModel):
    step_number: int
    title: str
    content: str
    step_type: str
    
# Schema for a complete ritual
class Ritual(BaseModel):
    session_id: str
    user_state: str  # "anxious", "unfocused", "stressed", etc.
    steps: List[RitualStep]
    created_at: datetime = datetime.now()
    
# Schema for storing session memory
class SessionMemory(BaseModel):
    session_id: str
    user_input: str
    user_state: str
    ritual_steps: List[str]
    rating: Optional[int] = None
    timestamp: datetime = datetime.now()
    
# Schema for ritual creation response
class RitualResponse(BaseModel):
    success: bool
    session_id: str
    ritual: Ritual
    message: str = "Ritual created successfully"
    
# Schema for feedback submission response
class FeedbackResponse(BaseModel):
    success: bool
    session_id: str
    rating: int
    message: str = "Feedback saved"
    