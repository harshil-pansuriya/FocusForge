import random
from datetime import datetime

from models.schemas import UserInput, Ritual, RitualStep
from services.ai_service import ai_service
from repository.pinecone_repository import pinecone_service
from config.logging import logger

class RitualArchitect:
    async def process_input(self, user_input: UserInput) -> Ritual:
        user_state = await ai_service.analyze_user_state(user_input.text)
        logger.info(f"User state for session {user_input.session_id}: {user_state}")
        
        similar_sessions = await pinecone_service.retrieve_similar_sessions(user_input.text, user_state)
        
        # Generate 4-7 steps using the AI service
        try:
            ritual_steps = await ai_service.generate_ritual_step(user_state['state'])
        except Exception as e:
            logger.error(f"Error generating ritual steps: {str(e)}")
            raise ValueError(f"Failed to generate ritual steps: {str(e)}")

        steps = []
        for i, step_content in enumerate(ritual_steps[:7], 1):  # Limit to max 7 steps
            steps.append(RitualStep(
                step_number=i,
                title=step_content["title"],
                content=step_content["content"],
                step_type=step_content["step_type"]
            ))
        
        # Optionally append high-rated steps from similar sessions
        for session in similar_sessions:
            if len(steps) >= 7:
                break
            if session.get("rating", 0) >= 4:
                try:
                    additional_steps = await ai_service.generate_ritual_step(user_state['state'])
                    for step_content in additional_steps:
                        if len(steps) >= 7:
                            break
                        # Check for duplicates in current steps to avoid redundancy
                        if step_content["step_type"] not in [step.step_type for step in steps]:
                            steps.append(RitualStep(
                                step_number=len(steps) + 1,
                                title=step_content["title"],
                                content=step_content["content"],
                                step_type=step_content["step_type"]
                            ))
                except Exception as e:
                    logger.error(f"Error generating additional step from similar session: {str(e)}")
                    continue
                
        ritual = Ritual(
            session_id=user_input.session_id,
            user_state=user_state['state'],
            steps=steps,
            created_at=datetime.now()
        )
        logger.info(f"Generated ritual for session {ritual.session_id} with {len(steps)} steps")
        return ritual