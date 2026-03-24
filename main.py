from db.postgres import init_db
from threading import Thread
from feeds.dhan_marketfeed import start_dhan_feed, start_broadcast_loop
import time


if __name__ == "__main__":
    # ✅ Init DB
    init_db()

    # ✅ Start Dhan Feed (collects data)
    Thread(target=start_dhan_feed, daemon=True).start()

    # ✅ Start HTTP Broadcast Loop (POST to your API)
    Thread(target=start_broadcast_loop, daemon=True).start()

    print("🚀 Live Market Data → Telemetry API Running")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Shutting down")