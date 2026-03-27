from typing import Dict
from fastapi import WebSocket
import asyncio
import time
class ConnectionManager:
    def __init__(self):
        self.agents: Dict[str, WebSocket] = {}
        self.frontends: Dict[str, WebSocket] = {}
        self.last_seen = {}
    async def connect_agent(self, device_id: str, websocket: WebSocket):
        await websocket.accept()
        if device_id in self.agents:
            print(f"[!] Replacing existing agent: {device_id}")
        self.agents[device_id] = websocket
        print(f"[+] Agent connected: {device_id}")

    async def connect_frontend(self, device_id: str, websocket: WebSocket):
        await websocket.accept()
        self.frontends[device_id] = websocket
        print(f"[+] Frontend connected: {device_id}")

    def disconnect_agent(self, device_id: str):
        self.agents.pop(device_id, None)
        print(f"[-] Agent disconnected: {device_id}")

    def disconnect_frontend(self, device_id: str):
        self.frontends.pop(device_id, None)
        print(f"[-] Frontend disconnected: {device_id}")

    async def send_to_agent(self, device_id: str, data: dict):
        ws = self.agents.get(device_id)
        if not ws:
            print(f"[!] Agent {device_id} not connected")
            return

        try:
            print("sending data to agent")
            await ws.send_json(data)
        except Exception as e:
            print(f"[!] Send failed (agent {device_id}): {e}")
            self.disconnect_agent(device_id)

    async def send_to_frontend(self, device_id: str, data: dict):
        ws = self.frontends.get(device_id)
        if not ws:
            print(f"[!] Frontend {device_id} not connected")
            return

        try:
            print("progress value: ",data["value"])
            await ws.send_json(data)
        except Exception as e:
            print(f"[!] Send failed (frontend {device_id}): {e}")
            self.disconnect_frontend(device_id)


    async def ping_agents(self):
        while True:
            for device_id in list(self.agents.keys()):
                try:
                    await self.send_to_agent(device_id, {"action": "ping"})
                except Exception as e:
                    print(f"[!] Ping failed for {device_id}: {e}")
            await asyncio.sleep(10)  # every 10 seconds
    async def cleanup_dead_agents(self):
        while True:
            now = time.time()

            for device_id in list(self.agents.keys()):
                last = self.last_seen.get(device_id, 0)

                if now - last > 15:  # 15 seconds timeout
                    print(f"[!] Agent {device_id} timed out")

                    self.disconnect_agent(device_id)

            await asyncio.sleep(5)
manager = ConnectionManager()