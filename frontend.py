import streamlit as st
import requests
from typing import Dict, Any, Optional
from datetime import datetime

# API Configuration
API_BASE_URL = "http://localhost:8080/api/v1"

# Streamlit page configuration (minimal)
st.set_page_config(
    page_title="FocusForge: Ritual Builder",
    layout="wide"
)

def init_session_state():
    """Initialize session state variables"""
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "ritual" not in st.session_state:
        st.session_state.ritual = None
    if "current_step" not in st.session_state:
        st.session_state.current_step = None
    if "progress" not in st.session_state:
        st.session_state.progress = None
    if "is_complete" not in st.session_state:
        st.session_state.is_complete = False
    if "ritual_generated" not in st.session_state:
        st.session_state.ritual_generated = False
    if "show_input" not in st.session_state:
        st.session_state.show_input = False
    if "show_steps" not in st.session_state:
        st.session_state.show_steps = False
    if "show_feedback" not in st.session_state:
        st.session_state.show_feedback = False
    if "feedback_submitted" not in st.session_state:
        st.session_state.feedback_submitted = False

def make_api_request(endpoint: str, method: str = "POST", data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
    # Make API request with error handling
    try:
        url = f"{API_BASE_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=20)
        else:
            response = requests.post(url, headers=headers, json=data, params=params, timeout=20)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to the server: {str(e)}. Please ensure the backend is running.")
        return {"success": False, "error": str(e)}

def display_ritual_step(step: Dict[str, Any]):
    # Display a single ritual step
    st.markdown(f"### Step {step['step_number']}: {step['title']}")
    st.markdown(f"*Type: {step['step_type']}*")
    st.markdown(f"**{step['content']}**")
    st.markdown("---")

def main():
    init_session_state()
    
    # Title
    st.title("FocusForge: AI Ritual Builder")
    
    # Show project information
    if not st.session_state.show_input and not st.session_state.ritual_generated and not st.session_state.show_steps and not st.session_state.show_feedback and not st.session_state.feedback_submitted:
        st.write("### Project Information")
        st.write("""
        **FocusForge** is designed to support your mental well-being by creating personalized rituals based on your emotional state.  
        - Share how you're feeling currently.  
        - We'll craft a unique ritual with steps, such as breathing exercises or journaling that will help you.
        - Follow the steps and provide feedback at the end to help us improve.  
        """)
        if st.button("Let's Begin"):
            st.session_state.show_input = True
            st.rerun()
    
    # Display Input section
    if st.session_state.show_input and not st.session_state.show_steps and not st.session_state.show_feedback and not st.session_state.feedback_submitted:
        st.write("### Enter Your Feelings")
        user_input = st.text_area(
            "Describe how you're feeling today:",
            height=100,
            placeholder="e.g., I'm feeling stressed and can't focus"
        )
        if st.button("Generate Ritual", disabled=not user_input.strip()):
            if user_input.strip():
                with st.spinner("Crafting your ritual..."):
                    response = make_api_request(
                        "/ritual",
                        data={"text": user_input, "session_id": str(datetime.now().timestamp())}
                    )
                    if response.get("success"):
                        st.session_state.session_id = response["session_id"]
                        st.session_state.ritual = response["ritual"]
                        st.session_state.ritual_generated = True
                        st.rerun()
                    else:
                        st.error(response.get("error", "Failed to generate ritual"))
            else:
                st.warning("Please enter how you're feeling to generate a ritual.")
        
        if st.session_state.ritual_generated and not st.session_state.show_steps:
            st.write("Your Ritual generated!")
            if st.button("Start Ritual"):
                with st.spinner("Loading first step..."):
                    step_response = make_api_request(f"/step/{st.session_state.session_id}", method="GET")
                    if step_response.get("success"):
                        st.session_state.current_step = step_response["current_step"]
                        st.session_state.progress = step_response["progress"]
                        st.session_state.is_complete = step_response["is_complete"]
                        st.session_state.show_steps = True
                        st.rerun()
                    else:
                        st.error(step_response.get("error", "Failed to start ritual"))

    # Show step-by-step ritual
    if st.session_state.show_steps and st.session_state.ritual and not st.session_state.show_feedback and not st.session_state.feedback_submitted:
        st.write(f"### Ritual for {st.session_state.ritual['user_state']}")
        
        if not st.session_state.is_complete and st.session_state.current_step:
            display_ritual_step(st.session_state.current_step)
            
            if st.button("Next Step"):
                with st.spinner("Loading next step..."):
                    response = make_api_request(f"/step/{st.session_state.session_id}/next")
                    if response.get("success"):
                        st.session_state.current_step = response.get("current_step")
                        st.session_state.progress = response["progress"]
                        st.session_state.is_complete = response.get("ritual_complete", False)
                        if st.session_state.is_complete:
                            st.write("Ritual completed!")
                            st.session_state.show_feedback = True
                        st.rerun()
                    else:
                        st.error(response.get("error", "Failed to advance step"))

    # Feedback section
    if st.session_state.show_feedback and not st.session_state.feedback_submitted:
        st.write("### Provide Feedback")
        rating = st.slider("Rate your ritual (1–5):", min_value=1, max_value=5, value=3)
        if st.button("Submit Feedback"):
            with st.spinner("Submitting feedback..."):
                response = make_api_request(
                    f"/feedback/{st.session_state.session_id}",
                    data={"rating": int(rating)}
                )
                if response.get("success"):
                    st.session_state.feedback_submitted = True
                    st.rerun()
                else:
                    st.error(response.get("error", "Failed to submit feedback"))

    # Final message after feedback
    if st.session_state.feedback_submitted:
        st.write("Submitted feedback, thank you!")

if __name__ == "__main__":
    main()