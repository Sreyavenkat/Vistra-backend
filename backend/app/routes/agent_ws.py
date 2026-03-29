from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket_manager import manager
from app.database import create_scan, complete_scan, save_file, update_file_action, get_user_by_device
from app.database import supabase
import time
router = APIRouter()
import uuid


@router.websocket("/ws/agent/{device_id}")
async def agent_ws(websocket: WebSocket, device_id: str):

    await manager.connect_agent(device_id, websocket)
    scan_id = None

    try:
        while True:
            message = await websocket.receive_json()
            print("🔥 FULL MESSAGE:", message)
            event = message.get("event")
            #print("🔥 RAW EVENT:", repr(event))
            #print("Event received")
            if event == "ping":
                manager.last_seen[device_id] = time.time()
            elif event == "START_SCAN":
                print("🔥 START_SCAN received in backend")
                #print(" scan_id from frontend:", scan_id)
                #user_id = get_user_by_device(device_id)
                #scan_id = create_scan(user_id, device_id)
                #scan_id = message.get("scan_id")
                scan_id = message.get("scan_id")
                print("SCAN_ID" , scan_id)
                user_id = "krishnan"
                device_id_db = message.get("device_id")
                print("device id: ", device_id_db)
                #layer = 1
                #print("Creating scan in DB:" , scan_id)
                create_scan(user_id, device_id_db, scan_id)
                print("🔥 create_scan called successfully")

                await manager.send_to_agent(device_id, {
                     "event": "SCAN_STARTED",
                     "scan_id": scan_id
                 })     

            elif event == "SCAN_PROGRESS":
                print("Forwarding progress to frontend: ", message)
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
                    "quarantined_files": value.get("quarantine", 0),
                    "malware_density": (
                        value.get("totalThreats", 0) /
                         max(1, value.get("totalThreats", 0) + value.get("safe", 0))
                    )
                }).execute()    

            elif event == "FILES_BATCH":
                scan_id = message.get("scan_id")
                files = message.get("files", [])

                print(f"📂 Inserting {len(files)} files into DB")

                for f in files:
                    save_file(
                        scan_id=scan_id,
                        file_path=f.get("file_path"),
                        file_name=f.get("file_name"),
                        action=f.get("action"),
                        file_score=f.get("severity"),  # ✅ correct field
                        layer="layer1",
                        quarantine_path=f.get("quarantined_path")
                    )

                # optional: forward to frontend
                await manager.send_to_frontend(device_id, {
                    "event": "FILES_BATCH",
                    "files": files
                })         
 
            elif event == "FILE_COUNT":
                await manager.send_to_frontend(device_id,message)
                

            elif event == "SCAN_COMPLETED":
                #complete_scan(message.get("scan_id"))
                #print("SACN_COMPLETED_MESSAGE:",message)
                scan_id = message.get("scan_id")

                if not scan_id:
                    print("SKIPPING DB UPDATE: NO SCAN_ID")
                else:    
                    complete_scan(scan_id)


            elif event == "DELETE_CONFIRMED":
                update_file_action(message["file_id"], message["action"])
                await manager.send_to_frontend(device_id, message)

    except WebSocketDisconnect:
        manager.disconnect_agent(device_id)