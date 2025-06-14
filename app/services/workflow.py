from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from datetime import datetime

from models.schemas import UserInput, Ritual, FeedbackResponse, SessionMemory
from usecases.ritual_architect import RitualArchitect
from usecases.ritual_guide import ritual_guide
from repository.pinecone_repository import pinecone_service
from config.logging import logger

class WorkflowState(TypedDict):
    session_id: str
    user_input: str
    ritual: Optional[Ritual]
    feedback: Optional[FeedbackResponse]
    
class WorkflowService:
    
    def __init__(self):
        self.architect= RitualArchitect()
        self.guide= ritual_guide
        self.graph= self._create_workflow()
        logger.info("Workflow Service initialized")
        
    def _create_workflow(self) -> StateGraph:
        graph= StateGraph(WorkflowState)
        
        async def input_node(state: WorkflowState) -> WorkflowState:
            logger.info(f"Processing input for session {state['session_id']}")
            try:
                user_input = UserInput(text=state['user_input'], session_id=state['session_id'])
                ritual = await self.architect.process_input(user_input)
                state['ritual'] = ritual
                
                session_memory = SessionMemory(
                    session_id=state['session_id'],
                    user_input=state['user_input'],
                    user_state=ritual.user_state,
                    ritual_steps=[step.step_type for step in ritual.steps],
                    rating=0,  # Initial rating
                    timestamp=datetime.now()
                )
                await pinecone_service.store_session(session_memory)
                return state
            except Exception as e:
                logger.error(f"Input processing error for session {state['session_id']}: {str(e)}")
                raise
            
        async def presentation_node(state: WorkflowState) -> WorkflowState:
            logger.info(f"Presenting ritual for session {state['session_id']}")
            try: 
                await self.guide.start_session(state['ritual'])
                return state
            except Exception as e:
                logger.error(f"Presentation error for session {state['session_id']}: {str(e)}")
                raise
            
        async def feedback_node(state: WorkflowState) -> WorkflowState:
            logger.info(f"Processing feedback for session {state['session_id']}")
            try:
                if state.get('feedback'):
                    await self.guide.collect_feedback(state['session_id'], state['feedback'])
                    return state
                logger.info(f"No feedback provided for session {state['session_id']}, skipping feedback node")
                return state
            except Exception as e:
                logger.error(f"Feedback error for session {state['session_id']}: {str(e)}")
                raise
        # Nodes
        graph.add_node("input", input_node)
        graph.add_node("presentation", presentation_node)
        graph.add_node("feedback_processing", feedback_node)
        
        # Edges
        graph.set_entry_point('input')
        graph.add_edge("input", "presentation")
        graph.add_conditional_edges(
            "presentation",
            lambda state: "feedback_processing" if state.get('feedback') else END,
            {"feedback_processing": "feedback_processing", END: END}
        )
        graph.add_edge("feedback_processing", END)
        
        return graph.compile()
    
    async def run_workflow(self, user_input: str, feedback: Optional[FeedbackResponse]= None) -> WorkflowState:
        session_id = pinecone_service.generate_session_id()
        logger.info(f"Starting workflow for session {session_id}")
        
        initial_state= WorkflowState(
            session_id=session_id,
            user_input= user_input,
            ritual= None,
            feedback=feedback
        )
        try:
            return await self.graph.ainvoke(initial_state)
        except Exception as e:
            logger.error(f"Workflow error for session {session_id} : {str(e)}")
            raise   