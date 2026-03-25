from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket_manager import manager
from app.database import create_scan, complete_scan, save_file, update_file_action, get_user_by_device
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
            print("Event received")
            if event == "ping":
                manager.last_seen[device_id] = time.time()
            elif event == "SCAN_START":
                user_id = get_user_by_device(device_id)
                scan_id = create_scan(user_id, device_id)

            elif event == "SCAN_PROGRESS":
                await manager.send_to_frontend(device_id, message)

            elif event == "FILE_RESULT":
                file_id = save_file(
                    scan_id=scan_id,
                    file_path=message["file_path"],
                    is_malicious=message["is_malicious"],
                    layer="layer1"
                )

                message["file_id"] = file_id
                await manager.send_to_frontend(device_id, message)

            elif event == "SCAN_COMPLETE":
                complete_scan(scan_id)
                await manager.send_to_frontend(device_id, message)

            elif event == "DELETE_CONFIRMED":
                update_file_action(message["file_id"], message["action"])
                await manager.send_to_frontend(device_id, message)

    except WebSocketDisconnect:
        manager.disconnect_agent(device_id)