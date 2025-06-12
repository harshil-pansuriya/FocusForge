# FocusForge: AI Ritual Builder

FocusForge is an AI-powered web application designed to enhance mental well-being by generating personalized rituals based on user's emotional states. It analyzes user input to identify states like anxiety, burnout, or low motivation, and creates tailored sequences of actionable steps (e.g., breathing exercises, journaling, gratitude) using Google Gemini AI, Pinecone for session storage, and a FastAPI backend with a Streamlit frontend.

## Features

- Emotional state analysis using Google Gemini to detect states like Anxiety, Self-Doubt, or Procrastination.
- Personalized ritual generation with unique steps tailored to the user's emotional needs.
- Session management and feedback storage using Pinecone vector database.
- Interactive Streamlit frontend for input, ritual navigation, and feedback submission.
- FastAPI backend with RESTful endpoints for ritual creation, step progression, and feedback.

## Tech Stack

- Framework: FastAPI
- Frontend: Streamlit
- Vector Store: Pinecone
- LLM: Google Gemini
- Embeddings: Sentence Transformers
- Workflow: LangGraph
- Validation: Pydantic
- Logging: Loguru
- Configuration: python-dotenv

## Setup

1. Clone the repository:

   ```
   git clone https://github.com/harshil-pansuriya/FocusForge.git
   cd FocusForge
   ```

2. Create and activate a virtual environment:

   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

   

4. Configure environment variables:

   Copy `.env.example` to `.env` and update:

   ```
   PINECONE_API_KEY=your_pinecone_key
   PINECONE_INDEX=your_pinecone_index_name
   GEMINI_API_KEY=your_google_key
   ```

5. Set up Pinecone index:

   Ensure your Pinecone index is created with 384 dimensions (matching `all-MiniLM-L6-v2`). Refer to Pinecone’s documentation for setup instructions.

## Running the Application

1. Start the FastAPI backend:

   ```
   python main.py
   ```

   The backend will be available at `http://localhost:8080`.

2. Start the Streamlit frontend:

   In a separate terminal, activate the virtual environment and run:

   ```
   streamlit run frontend.py
   ```

   The frontend will be available at `http://localhost:8501`.

## Usage

### Access the Frontend

- Navigate to `http://localhost:8501` in your browser.

### Input Emotional State

- Click "Let's Begin" and enter your current feelings.

### Generate and Follow Ritual

- Click "Generate Ritual" to create a personalized ritual.
- Press "Start Ritual" to begin, then follow each step.
- Click "Next Step" to progress through the ritual.

### Submit Feedback

- After completing the ritual, rate it (1–5) to provide feedback for improvement.

### API Endpoints

Access the FastAPI backend at `http://localhost:8080/api/v1`:

- **POST /ritual**

  Create a new ritual based on user input.

  ```
  curl -X POST -H "Content-Type: application/json" -d '{"text": "I feel anxious"}' http://localhost:8080/api/v1/ritual
  ```

  Response:

  ```
  {
    "success": true,
    "session_id": "uuid",
    "ritual": {...},
    "message": "Ritual created successfully"
  }
  ```

- **GET /step/{session_id}**

  Retrieve the current ritual step.

  ```
  curl http://localhost:8080/api/v1/step/{session_id}
  ```

- **POST /step/{session_id}/next**

  Advance to the next ritual step.

  ```
  curl -X POST http://localhost:8080/api/v1/step/{session_id}/next
  ```

- **POST /feedback/{session_id}**

  Submit feedback for a session.

  ```
  curl -X POST -H "Content-Type: application/json" -d '{"rating": 4}' http://localhost:8080/api/v1/feedback/{session_id}
  ```

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

Contributions are welcome!

## Contact

For questions or feedback, open an issue on the GitHub repository.
