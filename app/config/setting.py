from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict

class Settings(BaseSettings):
    
    groq_api_key: str
    
    pinecone_api_key: str
    pinecone_index: str 
    
    step_weights: Dict[str, Dict[str, float]]
    
    model_config= SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
Config= Settings()