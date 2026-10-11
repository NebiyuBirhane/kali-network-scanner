import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from scanner import async_arp_sweep

app = FastAPI(title="Kali Network Topology Scanner")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/scan")
async def websocket_scan_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        params = json.loads(data)
        target_cidr = params.get("target", "192.168.1.0/24")
        stealth_speed = float(params.get("speed", 0.05)) # Delay in seconds

        await websocket.send_text(json.dumps({
            "type": "status", 
            "message": f"Stealth scanning {target_cidr} (delay: {stealth_speed}s)..."
        }))

        # Stream discovered hosts back live with pacing
        async for host_info in async_arp_sweep(target_cidr, delay=stealth_speed):
            await websocket.send_text(json.dumps(host_info))

        await websocket.send_text(json.dumps({
            "type": "status", 
            "message": "Scan completed securely."
        }))
        
    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"Error in websocket loop: {e}")
