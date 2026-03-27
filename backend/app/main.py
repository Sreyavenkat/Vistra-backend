from fastapi import FastAPI,Request
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


@app.post("/deleteFile")
async def delete_file(request: Request):
    try:
        data = await request.json()
        event = "DELETE_FILE"
        scanId = data.get("scanId")
        fileName = data.get("fileName")
        filePath = data.get("filePath")
        message = {"event": event, "scanId": scanId, "fileName": fileName, "filePath": filePath}
        device_id = data.get("deviceId")
        # Debug log
        print(f"[+] Delete request: {data}")

        # send request to agent
        await manager.send_to_agent(device_id,message)
        # Example: delete file
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
@app.post("/keepFile")
async def keep_file(request: Request):
    try:
        data = await request.json()
        event = "KEEP_FILE"
        scanId = data.get("scanId")
        fileName = data.get("fileName")
        filePath = data.get("filePath")
        quarantinePath = "/home/kichu/projects/Vistra/Agents/Quarantine"
        message = {"event": event, 
                   "scanId": scanId, 
                   "fileName": fileName, 
                   "filePath": filePath, 
                   "quarantinePath": quarantinePath}
        device_id = data.get("deviceId")
        # Debug log
        print(f"[+] Delete request: {data}")

        # send request to agent
        await manager.send_to_agent(device_id,message)
        # Example: delete file
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)