import os
import time
from dhanhq import DhanContext, dhanhq


def main():
    print("======================================")
    print(" NIFTY INTELLIGENCE ENGINE v0.1")
    print(" Dhan Connection Test")
    print("======================================")

    # Read credentials from Render environment variables.
    client_id = os.getenv("DHAN_CLIENT_ID")
    access_token = os.getenv("DHAN_ACCESS_TOKEN")

    if not client_id:
        raise RuntimeError("DHAN_CLIENT_ID is missing.")

    if not access_token:
        raise RuntimeError("DHAN_ACCESS_TOKEN is missing.")

    print("Credentials found in environment.")
    print(f"Client ID: {client_id[:4]}****")

    # Current DhanHQ SDK authentication method.
    dhan_context = DhanContext(
        client_id,
        access_token
    )

    dhan = dhanhq(dhan_context)

    print("DhanHQ client initialized.")
    print("Testing Dhan account connection...")
    print("")

    try:
        # Read-only test.
        # This does NOT place, modify or cancel any order.
        positions = dhan.get_positions()

        print("======================================")
        print(" DHAN CONNECTION: SUCCESS")
        print("======================================")

        print("Positions API response received.")

        # We deliberately do not print the full response because
        # account/position information should not be unnecessarily
        # exposed in the Render logs.

        if isinstance(positions, dict):
            status = positions.get("status")
            print(f"API status: {status}")

        print("")
        print("No order has been placed.")
        print("No position has been modified.")
        print("Engine is running in READ-ONLY TEST MODE.")
        print("")

    except Exception as e:
        print("======================================")
        print(" DHAN CONNECTION: FAILED")
        print("======================================")
        print(f"Error type: {type(e).__name__}")
        print(f"Error: {e}")
        raise

    # Keep the Render worker alive.
    while True:
        print(
            "Engine alive:",
            time.strftime("%Y-%m-%d %H:%M:%S")
        )
        time.sleep(60)


if __name__ == "__main__":
    main())
