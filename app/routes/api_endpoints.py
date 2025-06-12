from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
from pydantic import BaseModel  
from models.schemas import UserInput, RitualResponse, FeedbackResponse
from controllers.input_controller import InputController
from config.logging import logger

router= APIRouter(prefix='/api/v1', tags=['ritual'])
controller= InputController()

class FeedbackRequest(BaseModel):
    rating: int

@router.post("/ritual", response_model= RitualResponse)
async def create_ritual(user_input: UserInput):
    logger.info(f"Received request to create ritual: {user_input.text}")
    try:
        response= await controller.process_user_input(user_input)
        return response
    except HTTPException as e:
        logger.error(f"HTTP error in create_ritual: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_ritual: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create ritual: {str(e)}"
        )
        
@router.get("/step/{session_id}", response_model= Dict[str, Any])
async def get_current_step(session_id: str):
    logger.info(f"Received request for current step: session {session_id}")
    try:
        response = await controller.get_current_step(session_id)
        return response
    except HTTPException as e:
        logger.error(f"HTTP error in get_current_step: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_current_step: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve step: {str(e)}"
        )
        
@router.post("/step/{session_id}/next", response_model= Dict[str, Any])
async def next_step(session_id: str):
    logger.info(f"Received request to advance step: session {session_id}")
    try:
        response = await controller.next_step(session_id)
        return response
    except HTTPException as e:
        logger.error(f"HTTP error in next_step: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in next_step: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to advance step: {str(e)}"
        )
    
@router.post('/feedback/{session_id}', response_model= FeedbackResponse)
async def submit_feedback(session_id: str, feedback_request: FeedbackRequest):
    logger.info(f"Received feedback request: session {session_id}, rating {feedback_request.rating}")
    try:
        if not 1 <= feedback_request.rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        response = await controller.submit_feedback(session_id, feedback_request.rating)
        return response
    except ValueError as e:
        logger.error(f"Validation error in submit_feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException as e:
        logger.error(f"HTTP error in submit_feedback: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in submit_feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save feedback: {str(e)}"
        )