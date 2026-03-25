from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.routes import agent_ws, frontend_ws, layer2, reports
import asyncio
from app.websocket_manager import manager
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent_ws.router)
app.include_router(frontend_ws.router)
app.include_router(layer2.router)
app.include_router(reports.router)

@app.on_event("startup")
async def start_cleanup():
    asyncio.create_task(manager.cleanup_dead_agents())
if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True)