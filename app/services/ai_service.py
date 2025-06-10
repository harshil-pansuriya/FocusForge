import json
from typing import Dict, Any, List

import google.generativeai as genai

from config.setting import Config
from config.logging import logger
from prompts.prompts import ANALYSIS_PROMPT, GENERATION_PROMPT

class AIMemoryService:
    def __init__(self):
        genai.configure(api_key=Config.gemini_api_key)
        self.gemini_client = genai.GenerativeModel('gemini-1.5-flash')
        self.state_prompt = ANALYSIS_PROMPT
        self.ritual_prompt = GENERATION_PROMPT

    def parse_response(self, response: str) -> Any:
        logger.debug(f"Raw LLM response: {response}")
        try:
            # Clean response
            cleaned = response.strip().strip('`').strip()
            if cleaned.startswith('json'):
                cleaned = cleaned[4:].strip()
            
            return json.loads(cleaned)
            
        except json.JSONDecodeError:
            logger.error(f"JSON decode error, raw response: {response}")
            return None
        except Exception as e:
            logger.error(f"Parse error: {str(e)}")
            return None

    async def analyze_user_state(self, user_input: str) -> Dict[str, Any]:
        prompt = self.state_prompt.format(user_input=user_input)
        
        try:
            response = await self.gemini_client.generate_content_async(
                contents=prompt,
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 100,
                    "response_mime_type": "application/json"
                }
            )
            
            result = self.parse_response(response.text)
            
            if result and isinstance(result, dict) and "state" in result and "confidence" in result:
                logger.info(f"Detected State: {result['state']} (confidence: {result['confidence']})")
                return result
            
            logger.error("Failed to analyze user state")
            raise ValueError("Unable to determine user state")
            
        except Exception as e:
            logger.error(f"Error analyzing user state: {str(e)}")
            raise ValueError(f"State analysis failed: {str(e)}")

    async def generate_ritual_step(self, user_state: str) -> List[Dict[str, str]]:
        prompt = self.ritual_prompt.format(user_state=user_state)
        
        try:
            response = await self.gemini_client.generate_content_async(
                contents=prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 500,
                    "response_mime_type": "application/json"
                }
            )
            
            result = self.parse_response(response.text)
            
            if result and isinstance(result, list):
                valid_steps = [step for step in result if all(key in step for key in ["title", "content", "step_type"])]
                if valid_steps:
                    logger.info(f"Generated {len(valid_steps)} ritual steps for state: {user_state}")
                    return valid_steps
            
            logger.error("Failed to generate ritual steps")
            raise ValueError("Unable to generate ritual steps")
            
        except Exception as e:
            logger.error(f"Error generating ritual steps: {str(e)}")
            raise ValueError(f"Ritual generation failed: {str(e)}")

ai_service = AIMemoryService()