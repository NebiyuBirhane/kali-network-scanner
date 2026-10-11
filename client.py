import asyncio
import websockets
import json

async def run_scan():
    uri = "ws://localhost:8000/ws/scan"
    async with websockets.connect(uri) as websocket:
        # Send target subnet to scan (replace with your actual local subnet if needed)
        payload = {"target": "192.168.1.0/24"}
        print(f"[*] Sending scan request for: {payload['target']}")
        await websocket.send(json.dumps(payload))

        # Listen for real-time streamed responses
        while True:
            try:
                response = await websocket.recv()
                data = json.loads(response)
                print("[+] Received:", data)
            except websockets.exceptions.ConnectionClosed:
                print("[-] Connection closed by server.")
                break

if __name__ == "__main__":
    asyncio.run(run_scan())
