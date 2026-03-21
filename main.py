from db.postgres import init_db
from threading import Thread
from feeds.dhan_marketfeed import start_dhan_feed
from websocket.frontend_ws import start_frontend_ws
import time

if __name__ == "__main__":
    init_db()  # ✅ ensure table exists

    Thread(target=start_frontend_ws, daemon=True).start()
    Thread(target=start_dhan_feed, daemon=True).start()

    print("🚀 Live Market Data System Running")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Shutting down")
