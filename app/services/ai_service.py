import json
from typing import List, Dict, Any

from groq import AsyncGroq

from config.setting import Config
from config.logging import logger

class AIMemoryService:
    def __init__(self):
        self.groq_client= AsyncGroq(api_key=Config.groq_api_key)
        
    async def analyze_user_state(self, user_input: str) -> Dict[str, Any]:
        prompt = f"""
        Analyze this user input and determine their emotional/cognitive state.
        User input: "{user_input}"
        
        Respond with only a JSON object containing:
        {{
            "state": "one of: anxious, unfocused, stressed, low_energy, overwhelmed, restless, scattered, tired",
            "confidence": "float between 0.0 and 1.0"
        }}
        """
        try:
            response= await self.groq_client.chat.completions.create(
                model="llama3-8b-8192",  
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=100
            )
            result= json.loads(response.choices()[0].message.content.strip())
            logger.info(f"Detected State: {result['state']} (confidense: {result['confidence']})")
            
            return result
        
        except Exception as e:
            logger.error(f"Error Analyzing User state: {str(e)}")
            return {'state':'unfocused', 'confidence':0.5}
        
    async def generate_ritual_step(self, step_type: str, user_state: str, step_number: int) -> Dict[str, str]:
        
        prompts = {
            "breathing": f"Create a simple breathing exercise for someone who feels {user_state}. Make it 1-2 minutes long.",
            "quote": f"Provide an inspiring, calming quote for someone who feels {user_state}.",
            "journaling": f"Create a brief journaling prompt for someone who feels {user_state}.",
            "affirmation": f"Write a positive affirmation for someone who feels {user_state}.",
            "physical": f"Suggest a quick 1-minute physical activity for someone who feels {user_state}."
        }
        
        prompt= f"""
        {prompts.get(step_type, prompts['breathing'])}
        Respond with only JSON Object:
        {{
            "title": "Brief Title (max 50 chars)",
            "content": "detailed instructions (max 200 chars)"
        }}        
        """
        try:
            response= await self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=150
            )
            usage = response.usage
            logger.info(f"Step {step_number} Generation ({step_type}) - Tokens: {usage.total_tokens} "
                    f"(prompt: {usage.prompt_tokens}, completion: {usage.completion_tokens})")
            
            result = json.loads(response.choices[0].message.content.strip())
            return result
            
        except Exception as e:
            logger.error(f"Error Generating step {step_number} :{str(e)}")
            return {
                "title": f"Step {step_number}",
                "content": "Take a moment to breathe deeply and relax."
            }
            
            
ai_service = AIMemoryService()
    