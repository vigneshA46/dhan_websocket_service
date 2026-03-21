import asyncio
import json
import websockets

clients = set()

async def handler(ws):
    clients.add(ws)
    print("✅ Client connected")

    try:
        async for _ in ws:
            pass

    except websockets.exceptions.ConnectionClosed:
        print("⚠️ Client disconnected")

    finally:
        clients.remove(ws)

async def broadcast(data):
    if not clients:
        return

    dead_clients = set()

    for client in clients:
        try:
            await client.send(json.dumps(data))
        except:
            dead_clients.add(client)

    # ✅ remove dead connections
    for dc in dead_clients:
        clients.discard(ws)


def start_frontend_ws():
    async def main():
        async with websockets.serve(handler, "0.0.0.0", 8765):
            print("🌐 Frontend WS running on ws://localhost:8765")
            await asyncio.Future()  # run forever

    asyncio.run(main())