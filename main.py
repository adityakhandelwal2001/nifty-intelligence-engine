import os
import time
from dhanhq import DhanContext, dhanhq


def log(message=""):
    print(message, flush=True)


log("======================================")
log(" NIFTY INTELLIGENCE ENGINE v0.1")
log(" DHAN CONNECTION TEST")
log("======================================")


client_id = os.getenv("DHAN_CLIENT_ID")
access_token = os.getenv("DHAN_ACCESS_TOKEN")


if not client_id:
    raise RuntimeError("DHAN_CLIENT_ID is missing.")

if not access_token:
    raise RuntimeError("DHAN_ACCESS_TOKEN is missing.")


log("Credentials found.")
log(f"Client ID: {client_id[:4]}****")
log("")


log("Creating DhanContext...")

dhan_context = DhanContext(
    client_id,
    access_token
)

log("DhanContext created.")

dhan = dhanhq(dhan_context)

log("DhanHQ client initialized.")
log("")


log("Calling Dhan Positions API...")
log("This is READ-ONLY.")
log("")


try:

    response = dhan.get_positions()

    log("======================================")
    log(" DHAN API RESPONSE RECEIVED")
    log("======================================")

    log(f"Response type: {type(response).__name__}")

    if isinstance(response, dict):
        log(f"API status: {response.get('status')}")
        log(f"Error type: {response.get('errorType')}")
        log(f"Error code: {response.get('errorCode')}")
        log(f"Error message: {response.get('errorMessage')}")

    log("")
    log("======================================")
    log(" DHAN CONNECTION TEST COMPLETE")
    log("======================================")
    log("No orders were placed.")
    log("No positions were modified.")
    log("")


except Exception as error:

    log("======================================")
    log(" DHAN API CALL FAILED")
    log("======================================")

    log(f"Error type: {type(error).__name__}")
    log(f"Error: {error}")

    raise


while True:

    log(
        "Engine alive: "
        + time.strftime("%Y-%m-%d %H:%M:%S")
    )

    time.sleep(60)
