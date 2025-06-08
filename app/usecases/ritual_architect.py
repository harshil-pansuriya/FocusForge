import random
from datetime import datetime

from models.schemas import UserInput, Ritual, RitualStep
from services.ai_service import ai_service
from repository.pinecone_repository import pinecone_service
from config.setting import Config
from config.logging import logger

class RitualArchitect:
    async def process_input(self, user_input: UserInput) -> Ritual:
        user_state= await ai_service.analyze_user_state(user_input.text )
        logger.info(f"User state for session {user_input.session_id} : {user_state}")
        
        similar_sessions= await pinecone_service.retrieve_similar_sessions(user_input.text, user_state)
        
        weights= Config.step_weights.get(user_state['state'], Config.step_weights['unfocused'])
        num_steps = random.randint(4, 7)
        step_types = random.choices(
            list(weights.keys()),
            weights=list(weights.values()),
            k=num_steps
        )
        
        steps=[]
        for i, step_type in enumerate(step_types, 1):
            step_content= await ai_service.generate_ritual_step(step_type, user_state['state'], i)
            steps.append(RitualStep(
                step_number=i,
                title=step_content["title"],
                content=step_content["content"],
                step_type=step_type
            ))
            
        for session in similar_sessions:
            if len(steps) >= 7:
                break
            
            if session.get("rating", 0) >= 4:
                for step in session.get("ritual_steps", []):
                    if step in weights and len(steps) < 7:
                        step_content = await ai_service.generate_ritual_step(step, user_state['state'], len(steps) + 1)
                        steps.append(RitualStep(
                            step_number=len(steps) + 1,
                            title=step_content["title"],
                            content=step_content["content"],
                            step_type=step
                        ))
        ritual= Ritual(
            session_id= user_input.session_id,
            user_state= user_state['state'],
            steps= steps[:7],
            created_at= datetime.now()
        )
        logger.info(f"Generated ritual for session {ritual.session_id} with {len(steps)} steps")
        return ritual