import os
import time
from dhanhq import dhanhq

CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

if not CLIENT_ID or not ACCESS_TOKEN:
    raise RuntimeError(
        "Missing DHAN_CLIENT_ID or DHAN_ACCESS_TOKEN environment variables."
    )

dhan = dhanhq(CLIENT_ID, ACCESS_TOKEN)

print("===================================")
print(" NIFTY INTELLIGENCE ENGINE v0.1")
print("===================================")
print("Dhan client initialized successfully.")
print("Client ID loaded:", CLIENT_ID[:4] + "****")
print("")

# We deliberately do NOT place orders.
# This version only confirms that the Dhan SDK initializes.

while True:
    print("Engine alive:", time.strftime("%Y-%m-%d %H:%M:%S"))
    time.sleep(30)
