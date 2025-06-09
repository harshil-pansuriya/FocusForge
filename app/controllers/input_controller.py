from typing import Dict, Any
from fastapi import HTTPException
from models.schemas import UserInput, RitualResponse, FeedbackResponse
from services.workflow import WorkflowService
from usecases.ritual_guide import ritual_guide
from config.logging import logger

class InputController:
    
    def __init__(self):
        self.workflow= WorkflowService()
        self.guide= ritual_guide
        logger.info("Input Controller initialized")
        
    async def process_user_input(self, user_input: UserInput) -> RitualResponse:
        logger.info(f"Processing user input: {user_input.text}")
        try:
            workflow_state= await self.workflow.run_workflow(user_input.text)
            ritual= workflow_state['ritual']
            
            return RitualResponse(
                success=True,
                session_id=ritual.session_id,
                ritual=ritual,
                message="Ritual created successfully"
            )
        except Exception as e:
            logger.error(f"Error processing user input: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to process input: {str(e)}")
        
    async def get_current_step(self, session_id: str) -> Dict[str, Any]:
        logger.info(f"Retrieving current step for session {session_id}")
        try:
            step_response = await self.guide.get_current_step(session_id)
            if not step_response['success']:
                raise ValueError(step_response['error'])
            return step_response
        except Exception as e:
            logger.error(f"Error retrieving step for session {session_id}: {str(e)}")
            raise HTTPException(status_code=404, detail=f"Failed to retrieve step: {str(e)}")

    async def next_step(self, session_id: str) -> Dict[str, Any]:
        logger.info(f"Advancing to next step for session {session_id}")
        try:
            step_response = await self.guide.next_step(session_id)
            if not step_response['success']:
                raise ValueError(step_response['error'])
            return step_response
        except Exception as e:
            logger.error(f"Error advancing step for session {session_id}: {str(e)}")
            raise HTTPException(status_code=404, detail=f"Failed to advance step: {str(e)}")
        
    async def submit_feedback(self, session_id: str, rating: int) -> FeedbackResponse:
        logger.info(f"Submitting feedback for session {session_id}")
        try:
            feedback = FeedbackResponse(success=True, session_id=session_id, rating=rating)
            feedback_response = await self.guide.collect_feedback(session_id, feedback)
            if not feedback_response['success']:
                raise ValueError(feedback_response['error'])
            return FeedbackResponse(
                success=True,
                session_id=session_id,
                rating=rating,
                message="Feedback saved"
            )
        except Exception as e:
            logger.error(f"Error submitting feedback for session {session_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to save feedback: {str(e)}")