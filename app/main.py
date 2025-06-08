from fastapi import FastAPI
import uvicorn
from typing import Dict, Any
from routes.api_endpoints import router
from config.logging import logger

app= FastAPI(title="FocusForge: Ritual Builder", version='1.0.0')

app.include_router(router)

@app.get("/", response_model=Dict[str, str])
async def root() -> Dict[str, Any]:
    return {"message": "FocusForge is running"} 

if __name__ == "__main__":
    logger.info("FocusForge FastAPI Server...")
    
    uvicorn.run(
        app,
        host='localhost',
        port=8080,
        log_level="info"
    )