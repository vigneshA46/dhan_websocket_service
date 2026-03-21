import asyncio
from dhanhq import marketfeed
from auth.dhan_token import get_access_token
from websocket.frontend_ws import broadcast
import os
import time

CLIENT_ID = os.getenv("CLIENT_ID")
LATEST_DATA = {}

instruments = [
    (marketfeed.NSE, "13", marketfeed.Quote),
    (marketfeed.NSE, "25", marketfeed.Quote),
    (marketfeed.IDX, "27", marketfeed.Quote),
    (marketfeed.IDX, "1", marketfeed.Quote),
    (marketfeed.IDX, "860", marketfeed.Quote)
]

INDEX_MAP = {
    "13": "NIFTY", 
    "25": "BANKNIFTY",
    "27": "FINNIFTY",
    "1": "MIDCAP",
    "860": "SENSEX"
}


def start_dhan_feed():
    # ✅ CRITICAL FIX: create event loop in this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    token = get_access_token()

    feed = marketfeed.DhanFeed(
        CLIENT_ID,
        token,
        instruments,
        version="v2"
    )

    print("📡 Dhan MarketFeed started")

    while True:
        try:
            feed.run_forever()
            data = feed.get_data()

            if not data:
                continue

            security_id = str(data.get("security_id"))

            payload = {
                "index": INDEX_MAP.get(security_id, security_id),
                "ltp": data.get("LTP"),
                "change": data.get("change"),
                "changePercent": data.get("changePercent"),
                "timestamp": data.get("exchangeTime")
            }
            LATEST_DATA[security_id] = payload

            
            

        except Exception as e:
            print("❌ Dhan WS error:", e)
            feed.run_forever()
            break


def start_broadcast_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    print("📡 Broadcast loop started")

    while True:
        try:
            if LATEST_DATA:
                for payload in LATEST_DATA.values():
                    loop.run_until_complete(broadcast(payload))
                    print("updated data",payload)

            time.sleep(1)  # ✅ every 1 second

        except Exception as e:
            print("❌ Broadcast error:", e)