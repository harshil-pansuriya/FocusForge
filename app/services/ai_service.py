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
        Analyze the following user input to determine their emotional or cognitive state. Consider keywords, tone, and context to identify the most prominent state. If multiple states are mentioned, prioritize the most intense or specific one based on the input's phrasing.

        User input: "{user_input}"

        Available states: anxious, unfocused, stressed, low energy, overwhelmed, restless, scattered, tired.

        Respond with a JSON object containing:
        {{
            "state": "the most likely state from the available options",
            "confidence": "float between 0.0 and 1.0, reflecting certainty based on input clarity"
        }}
        """
        try:
            response= await self.groq_client.chat.completions.create(
                model="llama3-8b-8192",  
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=100
            )
            raw_content = response.choices[0].message.content.strip()
            logger.debug(f"Raw response content: {raw_content}")
            if not raw_content:
                raise ValueError("Empty response from Groq API")
            result = json.loads(raw_content)
            logger.info(f"Detected State: {result['state']} (confidence: {result['confidence']})")
            return result
        except Exception as e:
            logger.error(f"Error Analyzing User state: {str(e)}")
            return {'state': 'unfocused', 'confidence': 0.5}
        
    async def generate_ritual_step(self, step_type: str, user_state: str, step_number: int) -> Dict[str, str]:
        
        prompts = {
            "breathing": f"Create a 1-2 minute breathing exercise tailored for someone feeling {user_state}. Include specific counts (e.g., inhale for 4 seconds) and imagery relevant to their state (e.g., releasing restlessness). Ensure the exercise is unique and avoids repetition with other breathing steps.",
            "quote": f"Provide a concise, inspiring quote (20-50 words) that directly addresses the feeling of {user_state}. The quote should resonate emotionally and offer actionable wisdom or comfort specific to their state.",
            "journaling": f"Create a focused journaling prompt for someone feeling {user_state}. The prompt should guide them to reflect on their state, identify causes, and plan a small actionable step. Keep it concise (50-100 words).",
            "affirmation": f"Write a short, empowering affirmation (10-20 words) for someone feeling {user_state}. It should counter their state with positivity and be specific to their emotional needs.",
            "physical": f"Suggest a 1-minute physical activity for someone feeling {user_state}. The activity should be simple, energizing, or calming as needed, and tailored to their state (e.g., stretching for low_energy, shaking for restless)."
        }
        
        prompt= f"""
        {prompts.get(step_type, prompts['breathing'])}
        Respond with only JSON Object:
        {{
            "title": "Brief title (max 50 chars, unique and state-specific)",
            "content": "Instructions or text (max 200 chars, clear and relevant)"
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
    