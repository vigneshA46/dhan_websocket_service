import asyncio
from dhanhq import marketfeed
from auth.dhan_token import get_access_token
from websocket.frontend_ws import broadcast
import os

CLIENT_ID = os.getenv("CLIENT_ID")

instruments = [
    (marketfeed.NSE, "13", marketfeed.Quote),
    (marketfeed.NSE, "25", marketfeed.Quote),
    (marketfeed.NSE, "27", marketfeed.Quote),
    (marketfeed.NSE, "1", marketfeed.Quote),
    (marketfeed.BSE, "860", marketfeed.Quote)
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

            security_id = str(data.get("securityId"))

            payload = {
                "index": INDEX_MAP.get(security_id, security_id),
                "ltp": data.get("LTP"),
                "change": data.get("change"),
                "changePercent": data.get("changePercent"),
                "timestamp": data.get("exchangeTime")
            }

            print("📊 Market Tick:", payload)
            loop.run_until_complete(broadcast(payload))

        except Exception as e:
            print("❌ Dhan WS error:", e)
            feed.disconnect()
            break