import os
import time

from dhanhq import DhanContext, dhanhq


print("======================================")
print(" NIFTY INTELLIGENCE ENGINE v0.1")
print(" DHAN CONNECTION TEST")
print("======================================")


client_id = os.getenv("DHAN_CLIENT_ID")
access_token = os.getenv("DHAN_ACCESS_TOKEN")


if not client_id:
    raise RuntimeError("DHAN_CLIENT_ID is missing.")

if not access_token:
    raise RuntimeError("DHAN_ACCESS_TOKEN is missing.")


print("Credentials found.")
print("Client ID:", client_id[:4] + "****")


# Current DhanHQ SDK authentication
dhan_context = DhanContext(
    client_id,
    access_token
)

dhan = dhanhq(dhan_context)


print("DhanHQ client initialized.")
print("Testing read-only connection...")
print("")


try:

    response = dhan.get_positions()

    print("======================================")
    print(" DHAN CONNECTION SUCCESS")
    print("======================================")

    print("Dhan API responded successfully.")
    print("API status:", response.get("status"))

    print("")
    print("READ-ONLY TEST")
    print("No orders were placed.")
    print("No positions were modified.")


except Exception as error:

    print("======================================")
    print(" DHAN CONNECTION FAILED")
    print("======================================")

    print("Error type:", type(error).__name__)
    print("Error:", error)

    raise


while True:

    print(
        "Engine alive:",
        time.strftime("%Y-%m-%d %H:%M:%S")
    )

    time.sleep(60)
