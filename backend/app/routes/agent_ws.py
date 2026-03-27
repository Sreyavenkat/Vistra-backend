from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket_manager import manager
from app.database import create_scan, complete_scan, save_file, update_file_action, get_user_by_device
from app.database import supabase
import time
router = APIRouter()

@router.websocket("/ws/agent/{device_id}")
async def agent_ws(websocket: WebSocket, device_id: str):

    await manager.connect_agent(device_id, websocket)
    scan_id = None

    try:
        while True:
            message = await websocket.receive_json()
            event = message.get("event")
            #print("Event received")
            if event == "ping":
                manager.last_seen[device_id] = time.time()
            elif event == "SCAN_START":
                user_id = get_user_by_device(device_id)
                scan_id = create_scan(user_id, device_id)

                await manager.send_to_agent(device_id, {
                     "event": "SCAN_STARTED",
                     "scan_id": scan_id
                 })     

            elif event == "SCAN_PROGRESS":
                await manager.send_to_frontend(device_id, message)

            elif event == "FILE_RESULT":
                scan_id = message.get("scan_id")
                value = message.get("value", {})
                supabase.table("reports").insert({
                    "scan_id": scan_id,
                    "files_scanned": value.get("totalThreats", 0) + value.get("safe", 0),
                    "infected_files": value.get("totalThreats", 0),
                    "clean_files": value.get("safe", 0),
                    "deleted_files": value.get("deletion", 0),
                    "quaratined_files": value.get("quarantine", 0),
                    "malware_density": (
                        value.get("totalThreats", 0) /
                         max(1, value.get("totalThreats", 0) + value.get("safe", 0))
                    )
                }).execute()         
 

                

            elif event == "SCAN_COMPLETED":
                complete_scan(message.get("scan_id"))


            elif event == "DELETE_CONFIRMED":
                update_file_action(message["file_id"], message["action"])
                await manager.send_to_frontend(device_id, message)

    except WebSocketDisconnect:
        manager.disconnect_agent(device_id)