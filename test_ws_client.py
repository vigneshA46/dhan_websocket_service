import asyncio
import json
import websockets
from datetime import datetime

WS_URL = "wss://dhanwebsocketservice-production-7979.up.railway.app"


async def test_ws():
    print("🔌 Connecting to", WS_URL)

    try:
        async with websockets.connect(WS_URL) as ws:
            print("✅ Connected")

            while True:
                msg = await ws.recv()
                data = json.loads(msg)

                print(
                    f"📈 {datetime.now().strftime('%H:%M:%S')} | "
                    f"{data['index']} | "
                    f"LTP={data['ltp']} | "
                    f"Δ={data['change']} ({data['changePercent']}%)"
                )

    except websockets.ConnectionClosed as e:
        print("❌ WebSocket closed:", e)
    except Exception as e:
        print("❌ Error:", e)


if __name__ == "__main__":
    asyncio.run(test_ws())