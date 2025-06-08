from typing import Dict, Any, Optional
from datetime import datetime

from models.schemas import Ritual, RitualStep, FeedbackResponse
from repository.pinecone_repository import pinecone_service
from config.logging import logger

class RitualGuide:
    def __init__(self):
        self.active_sessions= {}
        logger.info('Ritual Guide agent initialized')
        
    async def start_session(self, ritual: Ritual) -> Dict[str, Any]:
        session_id= ritual.session_id
        logger.info(f"Starting ritual session {session_id}")
        
        try:
            self.active_sessions[session_id] = {
                "ritual": ritual,
                "current_step": 1,
                "total_steps": len(ritual.steps),
                "started_at": datetime.now(),
                "completed_steps": []
            }
            first_step= await self._get_current_step(session_id)
            return{
                "success": True,
                "session_id": session_id,
                "total_steps": len(ritual.steps),
                "current_step": first_step,
                "progress": await self._get_progress(session_id),
                "messsage":f"Let's begin your {ritual.user_state} ritual!"
            }
        except Exception as e:
            logger.error(f"Error starting session {session_id}: {str(e)}")
            return {"success": False , "error": str(e)}
        
    async def get_current_step(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.active_sessions:
            logger.error(f"Session {session_id} not found")
            return {"success": False, "error": "Session not found"}
        
        try:
            current_step= await self._get_current_step(session_id)
            progress= await self._get_progress(session_id)
            return {
                "success": True,
                "session_id": session_id,
                "current_step": current_step,
                "progress": progress,
                "is_complete": await self._is_session_complete(session_id)
            }
        except Exception as e:
            logger.error(f"Error getting steps for {session_id} : {str(e)}")
            return {"success": False, "error": "Session not found"}
        
    async def next_step(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.active_sessions:
            return {"success": False, "error": "Session not found"}
        
        try:
            session= self.active_sessions[session_id]
            session['completed_steps'].append(session['current_step'])
            session["current_step"] += 1
            logger.info(f"Session {session_id}: moved to step {session['current_step']}")
            if await self._is_session_complete(session_id):
                return {
                    "success": True,
                    "session_id": session_id,
                    "ritual_complete": True,
                    "message": "Ritual completed! How did it go?",
                    "progress": await self._get_progress(session_id)
                }
            next_step = await self._get_current_step(session_id)
            return {
                "success": True,
                "session_id": session_id,
                "current_step": next_step,
                "progress": await self._get_progress(session_id),
                "ritual_complete": False
            }
        except Exception as e:
            logger.error(f"Error moving to next step for {session_id}: {str(e)}")
            return {"success": False, "error": str(e)}
        
    async def collect_feedback(self, session_id: str, feedback:FeedbackResponse) -> Dict[str, Any]:
        logger.info(f"Collecting feedback for session {session_id}")
        try:
            if session_id not in self.active_sessions:
                return {"success": False, "error": "Session not found in aactive sessions"}
            
            session = await pinecone_service.get_session(session_id)
            if not session:
                logger.error(f"Session {session_id} not found in Pinecone")
                return {"success": False, "error": "Session not found in storage"}
            
            save_success = await pinecone_service.update_session_rating(session_id, feedback.rating)
            if save_success:
                await self._cleanup_session(session_id)
                logger.info(f"Feedback saved for session {session_id}: rating {feedback.rating}")
                return {
                    "success": True,
                    "session_id": session_id,
                    "message": "Thank you for your feedback!",
                    "rating": feedback.rating
                }
            logger.error(f"Failed to save feedback for {session_id}")
            return {"success": False, "error": "Failed to save feedback"}
        except Exception as e:
            logger.error(f"Error collecting feedback for {session_id}: {str(e)}")
            return {"success": False, "error": str(e)}
            
    async def _get_current_step(self, session_id: str) -> Optional[RitualStep]:
        session = self.active_sessions[session_id]
        current_step_num = session["current_step"]
        for step in session['ritual'].steps:
            if step.step_number == current_step_num:
                return step
        return None
    
    async def _get_progress(self, session_id: str) -> dict:
        session = self.active_sessions[session_id]
        completed= len(session['completed_steps'])
        total= session['total_steps']
        return{
            "completed_steps": completed,
            "total_steps": total,
            "percentage": int((completed / total ) * 100 ) if total > 0 else 0,
            "current_step_number": session['current_step']
        }
    
    async def _is_session_complete(self, session_id: str) -> bool:
        session= self.active_sessions[session_id]
        return session['current_step'] > session['total_steps']
    
    async def _cleanup_session(self, session_id: str):
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info("Session {session_id} Cleaned up")