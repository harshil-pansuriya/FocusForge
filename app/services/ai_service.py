import json
import re
from typing import Dict, Any

import google.generativeai as genai

from config.setting import Config
from config.logging import logger

class AIMemoryService:
    def __init__(self):
        genai.configure(api_key=Config.gemini_api_key)
        self.gemini_client = genai.GenerativeModel('gemini-1.5-pro')
        
    def _clean_response(self, raw_content: str) -> str:
        """Remove markdown code fences and extra whitespace from API response."""
        return re.sub(r'^```json\s*|\s*```$', '', raw_content, flags=re.MULTILINE).strip()

    async def analyze_user_state(self, user_input: str) -> Dict[str, Any]:
        prompt = f"""
            You are an expert in psychological and emotional state analysis. 
            Analyze the user input to identify the primary emotional or cognitive state(s). 
            Focus on keywords, tone, and context to infer a precise, descriptive state but perfect and concise (e.g., 'work-related anxiety'). 
            Combine multiple states for better ritual generation if needed (e.g., 'stress and concern'). 
            Avoid generic terms like 'neutral' unless relevant. 
            Provide a confidence score (0.0-1.0).

            Input: "{user_input}"

            Output a valid JSON object:
            {{
                "state": "<inferred state>",
                "confidence": <float 0.0-1.0>
            }}

            Ensure valid JSON without markdown code fences.
        """
        try:
            response = await self.gemini_client.generate_content_async(
                contents=prompt,
                generation_config={
                    "temperature": 0.1, 
                    "max_output_tokens": 100
                }
            )
            cleaned_content = self._clean_response(response.text)
            result = json.loads(cleaned_content)
            logger.info(f"Detected State: {result['state']} (confidence: {result['confidence']})")
            return result
        except Exception as e:
            logger.error(f"Error analyzing user state: {str(e)}")
            raise ValueError(f"Failed to analyze user state: {str(e)}")
        
    async def generate_ritual_step(self, user_state: str, step_number: int, previous_steps: list[Dict[str, str]]) -> Dict[str, str]:
        previous_titles = [step["title"] for step in previous_steps]
        previous_types = [step["step_type"] for step in previous_steps]
        
        prompt = f"""
            You are a creative ritual designer. For a user in state '{user_state}', generate a unique, actionable ritual step (3-4 minutes) tailored to their needs and also give detailed so it can help in better way.
            Choose a distinct activity type from: breathing, journaling, affirmation, physical movement, mindfulness, gratitude, visualization, grounding and etc according to you as per need. 
            Ensure the step is specific, emotionally resonant, and avoids repetition with previous steps: {', '.join(previous_titles)} (types: {', '.join(previous_types)}).

            Output a valid JSON object:
            {{
                "title": "<unique title (max 50 chars, state-specific)>",
                "content": "<instructions (150-200 chars, tailored to state)>",
                "step_type": "<activity type>"
            }}

            Ensure valid JSON without markdown code fences.
        """
        try:
            response = await self.gemini_client.generate_content_async(
                contents=prompt,
                generation_config={
                    "temperature": 0.3, 
                    "max_output_tokens": 150
                }
            )
            cleaned_content = self._clean_response(response.text)
            result = json.loads(cleaned_content)
            if result["step_type"] in previous_types:
                raise ValueError(f"Step {step_number} has duplicate type: {result['step_type']}")
            logger.info(f"Step {step_number} Generated - Title: {result['title']}, Type: {result['step_type']}")
            return result
        except Exception as e:
            logger.error(f"Error generating step {step_number}: {str(e)}")
            raise ValueError(f"Failed to generate step {step_number}: {str(e)}")

ai_service = AIMemoryService()