import asyncio
from dhanhq import marketfeed
from auth.dhan_token import get_access_token
from websocket.frontend_ws import broadcast
import time
import os

CLIENT_ID = os.getenv("CLIENT_ID")
INDEX_STATE = {}

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

            if not data or "security_id" not in data:
                continue

            security_id = str(data["security_id"])
            index_name = INDEX_MAP.get(security_id)

            if not index_name:
                continue

            # init state
            if security_id not in INDEX_STATE:
                INDEX_STATE[security_id] = {
                    "ltp": None,
                    "prev_close": None,
                    "time": None
                }

            state = INDEX_STATE[security_id]

            # ---- Quote LTP ----
            if data.get("type") == "Quote Data" and "LTP" in data:
                state["ltp"] = float(data["LTP"])
                state["time"] = data.get("LTT")

            # ---- Previous Close ----
            elif data.get("type") == "Previous Close":
                state["prev_close"] = float(data["prev_close"])
                continue

            # Emit only when both exist
            if state["ltp"] is not None and state["prev_close"] is not None:
                change = round(state["ltp"] - state["prev_close"], 2)
                change_percent = round(
                    (change / state["prev_close"]) * 100, 2
                )

                payload = {
                    "index": index_name,
                    "ltp": state["ltp"],
                    "change": change,
                    "changePercent": change_percent,
                    "time": state["time"]
                }

                print("📊 NORMALIZED:", payload)
                loop.run_until_complete(broadcast(payload))

        except Exception as e:
            print("❌ Dhan WS error:", e)
            print("🔁 Reconnecting in 5 seconds...")
            time.sleep(5)
            continue