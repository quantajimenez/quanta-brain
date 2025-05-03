# quanta/clock/clock.py

from datetime import datetime
import pytz

def init():
    print("🕒 Clock initialized.")

    # Get current UTC time
    utc_now = datetime.utcnow()
    print("🌐 UTC Time:", utc_now.strftime("%Y-%m-%d %H:%M:%S"))

    # Get current Central Time (America/Chicago timezone)
    ct_tz = pytz.timezone("America/Chicago")
    ct_now = datetime.now(ct_tz)
    print("🇺🇸 Central Time (CT):", ct_now.strftime("%Y-%m-%d %H:%M:%S"))
