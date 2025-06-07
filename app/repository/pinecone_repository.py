import uuid
from typing import List, Dict, Any
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

from app.models.schemas import SessionMemory
from app.config.logging import logger
from app.config.setting import Config


class PineconeRespository:
    def __init__(self):
        self.pc= Pinecone(api_key= Config.pinecone_api_key)
        self.index= self.pc.index(Config.pinecone_index)
        
        self.embedding_model= SentenceTransformer("all-MiniLM-L6-v2")
        
    async def generate_embeddings(self, text: str) -> List[float]:
        try:
            embedding= self.embedding_model.encode(text).tolist()
            logger.debug(f"Created embedding with {len(embedding)} dimensions")
            return embedding
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            return []
        
    async def store_session(self, session_memory: SessionMemory) -> bool:
        try:
            memory_text = f"{session_memory.user_input} {session_memory.user_state} {' '.join(session_memory.ritual_steps)}"
            embedding = await self.generate_embeddings(memory_text)
            if not embedding:
                logger.error("Failed to create embedding for session")
                return False
            
            self.index.upsert(
                vectors=[{
                    'id': session_memory.session_id,
                    'values': embedding,
                    'metadata': {
                        'user_input': session_memory.user_input,
                        'user_state': session_memory.user_state,
                        'ritual_steps': session_memory.ritual_steps,
                        'rating': session_memory.rating,
                        'timestamp': session_memory.timestamp.isoformat()
                    }
                }])
            logger.info(f"Session {session_memory.session_id} saved to memory")
            return True
            
        except Exception as e:
            logger.error(f"Error saving session memory: {str(e)}")
            return False
        
    async def retrieve_similar_sessions(self, user_input: str, user_state: str, top_k: int = 3) -> List[Dict[str, Any]]:
        try:
            query_text= f"{user_input} {user_state}"
            embedding= await self.generate_embeddings(query_text)
            results= self.index.query(
                vector= embedding,
                top_k= top_k,
                include_metadata= True,
                filter= {'rating': {"$gte: 3"}}
            )
            
            sessions= [{
                'session_id': match.id,
                'score': match.score,
                'user_state': match.metadata.get('user_state'),
                "ritual_steps": match.metadata.get("ritual_steps", []),
                "rating": match.metadata.get("rating")
            } for match in results.matches]
            logger.info(f"Retrieved {len(sessions)} similar sessions")
            return sessions
        except Exception as e:
            logger.error(f"Session retrieval error: {str(e)}")
            return []
        
    def generate_session_id(self) -> str:
        return str(uuid.uuid4())        # Generate Unique session id

pinecone_service= PineconeRespository()