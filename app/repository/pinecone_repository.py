import uuid
from typing import List, Dict, Any, Optional
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

from models.schemas import SessionMemory
from config.logging import logger
from config.setting import Config


class PineconeRespository:
    def __init__(self):
        self.pc= Pinecone(api_key= Config.pinecone_api_key)
        self.index= self.pc.Index(Config.pinecone_index)
        
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
        
    async def update_session_rating(self, session_id: str, rating: int) -> bool:
        try:
            session = await self.get_session(session_id)
            if not session:
                logger.error(f"Session {session_id} not found for rating update")
                return False
            self.index.upsert(
                vectors=[{
                    'id': session_id,
                    'values': await self.generate_embeddings(
                        f"{session['user_input']} {session['user_state']} {' '.join(session['ritual_steps'])}"
                    ),
                    'metadata': {
                        'user_input': session['user_input'],
                        'user_state': session['user_state'],
                        'ritual_steps': session['ritual_steps'],
                        'rating': rating,
                        'timestamp': session['timestamp']
                    }
                }]
            )
            logger.info(f"Updated rating for session {session_id}: {rating}")
            return True
        except Exception as e:
            logger.error(f"Error updating session rating for {session_id}: {str(e)}")
            return False
        
    async def retrieve_similar_sessions(self, user_input: str, user_state: Dict[str, Any], top_k: int = 3) -> List[Dict[str, Any]]:
        try:
            query_text= f"{user_input} {user_state['state']}"
            embedding= await self.generate_embeddings(query_text)
            results= self.index.query(
                vector= embedding,
                top_k= top_k,
                include_metadata= True,
                filter= {'rating': {"$gte": 3}}
            )
            
            sessions= [{
                'session_id': match['id'],
                'score': match['score'],
                'user_state': match['metadata'].get('user_state'),
                "ritual_steps": match['metadata'].get("ritual_steps", []),
                "rating": match['metadata'].get("rating")
            } for match in results['matches']]
            logger.info(f"Retrieved {len(sessions)} similar sessions")
            return sessions
        except Exception as e:
            logger.error(f"Session retrieval error: {str(e)}")
            return []
        
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        try:
            result = self.index.fetch(ids=[session_id])
            if result.vectors and session_id in result.vectors:
                return result.vectors[session_id]['metadata']
            logger.error(f"Session {session_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error fetching session {session_id}: {str(e)}")
            return None    
    
    def generate_session_id(self) -> str:
        return str(uuid.uuid4())        # Generate Unique session id

pinecone_service= PineconeRespository()     