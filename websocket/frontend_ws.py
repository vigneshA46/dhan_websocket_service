import asyncio
import json
import websockets

CLIENTS = set()


async def handler(ws):
    CLIENTS.add(ws)
    print("🟢 Frontend connected")

    try:
        async for _ in ws:
            pass
    finally:
        CLIENTS.remove(ws)
        print("🔴 Frontend disconnected")


async def broadcast(data):
    if not CLIENTS:
        return

    message = json.dumps(data)
    await asyncio.gather(
        *[client.send(message) for client in CLIENTS]
    )


def start_frontend_ws():
    async def main():
        async with websockets.serve(handler, "0.0.0.0", 8765):
            print("🌐 Frontend WS running on ws://localhost:8765")
            await asyncio.Future()  # run forever

    asyncio.run(main())