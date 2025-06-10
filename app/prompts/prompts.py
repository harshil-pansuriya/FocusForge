ANALYSIS_PROMPT="""
You are an AI analyzing user input to determine their mental state from the following predefined states: Anxiety and Overwhelm, Low Motivation / Apathy, Burnout, Sadness, Self-Doubt or Insecurity, Social Withdrawal, Procrastination Loop, Inner Critic or Shame, Fear of Failure, Decision Fatigue.

Task: Analyze the user's input text to identify the most relevant mental state. Return a JSON object with the identified state and a confidence score (0.0 to 1.0).

Instructions:
- Interpret the user's input for emotional cues, tone, and context.
- Match the input to one of the predefined states.
- Assign a confidence score (e.g., 0.9 for strong match, 0.5 for unclear).
- If unclear, return {{"state": "unknown", "confidence": 0.5}}.
- Return only valid JSON with keys "state" and "confidence".

Input: {user_input}

Output Example:
{{
  "state": "Self-Doubt or Insecurity", 
  "confidence": 0.9
  }}

JSON Response:"""

GENERATION_PROMPT="""
You are an AI generating a personalized ritual for a user based on their mental state to promote emotional well-being. 
The possible mental states: Anxiety and Overwhelm, Low Motivation / Apathy, Burnout, Sadness, Self-Doubt or Insecurity, Social Withdrawal, Procrastination Loop, Inner Critic or Shame, Fear of Failure, Decision Fatigue. 
The possible ritual steps are: Breathing, Affirmation, Journaling, Movement, Visualization, Music, Micro-Action, Mindfulness, Gratitude, Reflection, Intention Setting, Mantra Chanting, Creative Expression.

Task: Generate a sequence of 4 to 7 ritual steps tailored to the user's mental state, ensuring each step is unique and addresses the emotional needs of the specified state. Return a JSON array where each element contains the step's title, content, and type.

Instructions:
- Use the provided user state to select 4 to 7 ritual steps.
- Ensure each step_type is unique within the sequence.
- For each step:
  - Create a title (max 5 words).
  - Provide detailed content (2-4 sentences) specific to the user's mental state.
  - Ensure content is empathetic and actionable.
- Prioritize a cohesive flow (calming to empowering).
- Return only valid JSON array with keys "title", "content", "step_type".

Input:
- User state: {user_state}

Output Example:
[
  {{
    "title": "Deep Calm Breathing", 
    "content": "Sit comfortably and inhale deeply through your nose for 5 seconds, feeling your chest expand. Hold for 3 seconds, then exhale slowly for 7 seconds, releasing tension. Repeat 6 times, focusing on the rhythm to quiet your anxious mind.", 
    "step_type": "Breathing"
  }},
  {{
    "title": "Positive Self Affirmation", 
    "content": "Repeat softly to yourself: 'I am capable and calm.' Say it 5 times, letting each word sink in to counter overwhelm. Picture yourself handling challenges with ease.", 
    "step_type": "Affirmation"
  }},
  {{
    "title": "Gratitude Moment", 
    "content": "Write down three things you're grateful for today, no matter how small, like a warm drink or a kind word. Reflect on how they bring light to your day, shifting focus from stress. Keep the list nearby for comfort.", 
    "step_type": "Gratitude"
  }}
]

JSON Response: """