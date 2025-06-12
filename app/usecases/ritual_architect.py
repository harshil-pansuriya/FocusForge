from datetime import datetime

from models.schemas import UserInput, Ritual, RitualStep
from services.ai_service import ai_service
from config.logging import logger

class RitualArchitect:
    async def process_input(self, user_input: UserInput) -> Ritual:
        # Analyze user input to determine emotional state
        user_state = await ai_service.analyze_user_state(user_input.text)
        logger.info(f"User state for session {user_input.session_id}: {user_state}")
        
        # Generate ritual steps tailored to the user state
        try:
            ritual_steps = await ai_service.generate_ritual_step(user_state['state'])
        except Exception as e:
            logger.error(f"Error generating ritual steps: {str(e)}")
            raise ValueError(f"Failed to generate ritual steps: {str(e)}")

        # Convert generated steps to RitualStep objects
        steps = [
            RitualStep(
                step_number=i + 1,
                title=step_content["title"],
                content=step_content["content"],
                step_type=step_content["step_type"]
            )
            for i, step_content in enumerate(ritual_steps)
        ]
        
        # Create and return the ritual
        ritual = Ritual(
            session_id=user_input.session_id,
            user_state=user_state['state'],
            steps=steps,
            created_at=datetime.now()
        )
        logger.info(f"Generated ritual for session {ritual.session_id} with {len(steps)} steps")
        return ritual