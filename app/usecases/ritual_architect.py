import random
from datetime import datetime

from models.schemas import UserInput, Ritual, RitualStep
from services.ai_service import ai_service
from repository.pinecone_repository import pinecone_service
from config.logging import logger

class RitualArchitect:
    async def process_input(self, user_input: UserInput) -> Ritual:
        user_state= await ai_service.analyze_user_state(user_input.text )
        logger.info(f"User state for session {user_input.session_id} : {user_state}")
        
        similar_sessions= await pinecone_service.retrieve_similar_sessions(user_input.text, user_state)
        
        num_steps = random.randint(4, 7)
    
        steps=[]
        previous_steps = []
        
        for i in range(1, num_steps + 1):
            step_content = await ai_service.generate_ritual_step(user_state['state'], i, previous_steps)
            steps.append(RitualStep(
                step_number=i,
                title=step_content["title"],
                content=step_content["content"],
                step_type=step_content["step_type"]
            ))
            previous_steps.append(step_content)
            
        for session in similar_sessions:
            if len(steps) >= 7:
                break
            if session.get("rating", 0) >= 4:
                step_content = await ai_service.generate_ritual_step(user_state['state'], len(steps) + 1, previous_steps)
                steps.append(RitualStep(
                    step_number=len(steps) + 1,
                    title=step_content["title"],
                    content=step_content["content"],
                    step_type=step_content["step_type"]
                ))
                previous_steps.append(step_content)
                
        ritual = Ritual(
            session_id=user_input.session_id,
            user_state=user_state['state'],
            steps=steps[:7],
            created_at=datetime.now()
        )
        logger.info(f"Generated ritual for session {ritual.session_id} with {len(steps)} steps")
        return ritual