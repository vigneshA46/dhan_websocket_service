from datetime import datetime, time
import pytz

IST = pytz.timezone("Asia/Kolkata")

def is_market_open():
    now = datetime.now(IST)

    # Monday (0) to Friday (4)
    if now.weekday() > 4:
        return False

    start = time(9, 15)
    end = time(15, 30)

    return start <= now.time() <= end