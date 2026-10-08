import os
import time
from datetime import date, timedelta

from dhanhq import DhanContext, dhanhq


def log(message=""):
    print(message, flush=True)


def main():

    log("==============================================")
    log(" NIFTY INTELLIGENCE ENGINE v0.2.1")
    log(" DIRECT OPTION CHAIN TEST")
    log("==============================================")

    client_id = os.getenv("DHAN_CLIENT_ID")
    access_token = os.getenv("DHAN_ACCESS_TOKEN")

    if not client_id:
        raise RuntimeError("DHAN_CLIENT_ID is missing.")

    if not access_token:
        raise RuntimeError("DHAN_ACCESS_TOKEN is missing.")

    log("Credentials found.")
    log(f"Client ID: {client_id[:4]}****")
    log("")

    # --------------------------------------------------
    # Dhan connection
    # --------------------------------------------------

    dhan_context = DhanContext(
        client_id,
        access_token
    )

    dhan = dhanhq(dhan_context)

    log("DhanHQ client initialized.")
    log("")

    # --------------------------------------------------
    # NIFTY configuration
    # --------------------------------------------------

    NIFTY_SECURITY_ID = 13
    NIFTY_SEGMENT = "IDX_I"

    log("NIFTY Security ID:",)
    log(str(NIFTY_SECURITY_ID))
    log(f"Segment: {NIFTY_SEGMENT}")
    log("")

    # --------------------------------------------------
    # Known upcoming NIFTY expiry candidates
    #
    # We deliberately bypass expiry_list(), because
    # Dhan's expiry-list endpoint has shown failures
    # for NIFTY even with valid authentication.
    # --------------------------------------------------

    candidate_expiries = [
        "2026-10-13",
        "2026-10-20",
        "2026-10-27",
        "2026-11-03",
        "2026-11-10",
        "2026-11-17",
        "2026-11-24",
    ]

    successful_chain = None
    selected_expiry = None

    # --------------------------------------------------
    # Try option-chain directly
    # --------------------------------------------------

    for expiry in candidate_expiries:

        log(f"Trying option chain: {expiry}")

        try:

            response = dhan.option_chain(
                under_security_id=NIFTY_SECURITY_ID,
                under_exchange_segment=NIFTY_SEGMENT,
                expiry=expiry
            )

            if (
                isinstance(response, dict)
                and response.get("status") == "success"
                and response.get("data")
            ):

                successful_chain = response
                selected_expiry = expiry

                log(f"SUCCESS: {expiry}")
                break

            else:

                log(
                    f"Rejected: {response}"
                )

        except Exception as error:

            log(
                f"Request error for {expiry}: "
                f"{type(error).__name__}: {error}"
            )

        # Dhan Option Chain API has a rate limit.
        time.sleep(4)


    # --------------------------------------------------
    # No successful expiry
    # --------------------------------------------------

    if successful_chain is None:

        log("")
        log("==============================================")
        log(" OPTION CHAIN COULD NOT BE RETRIEVED")
        log("==============================================")
        log("")
        log(
            "Authentication is working, but none of the "
            "candidate expiries returned an option chain."
        )

        raise RuntimeError(
            "No successful NIFTY option-chain response."
        )


    # --------------------------------------------------
    # Extract option-chain data
    # --------------------------------------------------

    data = successful_chain.get("data", {})

    underlying_price = float(
        data.get("last_price", 0)
    )

    option_chain = data.get("oc", {})

    if not option_chain:
        raise RuntimeError(
            "Option-chain response contains no strikes."
        )


    log("")
    log("==============================================")
    log(" OPTION CHAIN RECEIVED SUCCESSFULLY")
    log("==============================================")

    log(f"NIFTY LTP: {underlying_price:.2f}")
    log(f"Expiry: {selected_expiry}")
    log(f"Strikes received: {len(option_chain)}")
    log("")


    # --------------------------------------------------
    # Find ATM
    # --------------------------------------------------

    strikes = []

    for strike in option_chain.keys():

        try:
            strikes.append(float(strike))
        except ValueError:
            pass


    if not strikes:
        raise RuntimeError(
            "No valid strikes found."
        )


    atm_strike = min(
        strikes,
        key=lambda x: abs(x - underlying_price)
    )

    log(f"ATM strike: {atm_strike:.0f}")
    log("")


    # --------------------------------------------------
    # Display ATM +/- 5 strikes
    # --------------------------------------------------

    strikes.sort()

    atm_index = strikes.index(atm_strike)

    start = max(0, atm_index - 5)
    end = min(len(strikes), atm_index + 6)

    selected_strikes = strikes[start:end]


    log("==============================================================")
    log(" NIFTY OPTION CHAIN")
    log("==============================================================")

    log(
        "STRIKE | "
        "CE LTP | CE OI | CE PREV OI | CE IV | "
        "PE LTP | PE OI | PE PREV OI | PE IV"
    )

    log("-" * 100)


    for strike in selected_strikes:

        strike_key = f"{strike:.6f}"

        item = option_chain.get(strike_key)

        if item is None:
            item = option_chain.get(str(strike))

        if item is None:
            continue


        ce = item.get("ce", {})
        pe = item.get("pe", {})


        log(
            f"{strike:6.0f} | "
            f"{ce.get('last_price', 0):>6} | "
            f"{ce.get('oi', 0):>10} | "
            f"{ce.get('previous_oi', 0):>10} | "
            f"{ce.get('implied_volatility', 0):>6} | "
            f"{pe.get('last_price', 0):>6} | "
            f"{pe.get('oi', 0):>10} | "
            f"{pe.get('previous_oi', 0):>10} | "
            f"{pe.get('implied_volatility', 0):>6}"
        )


    # --------------------------------------------------
    # Detailed ATM data
    # --------------------------------------------------

    log("")
    log("==============================================================")
    log(" ATM DETAILED DATA")
    log("==============================================================")


    atm_item = option_chain.get(
        f"{atm_strike:.6f}"
    )

    if atm_item is None:
        atm_item = option_chain.get(
            str(atm_strike)
        )


    if atm_item:

        for option_type, label in [
            ("ce", "CALL"),
            ("pe", "PUT")
        ]:

            option = atm_item.get(
                option_type,
                {}
            )

            greeks = option.get(
                "greeks",
                {}
            )

            log("")
            log(label)

            log(
                f"  LTP:        "
                f"{option.get('last_price')}"
            )

            log(
                f"  OI:         "
                f"{option.get('oi')}"
            )

            log(
                f"  Previous OI: "
                f"{option.get('previous_oi')}"
            )

            log(
                f"  Volume:     "
                f"{option.get('volume')}"
            )

            log(
                f"  IV:         "
                f"{option.get('implied_volatility')}"
            )

            log(
                f"  Bid:        "
                f"{option.get('top_bid_price')}"
            )

            log(
                f"  Ask:        "
                f"{option.get('top_ask_price')}"
            )

            log(
                f"  Bid Qty:    "
                f"{option.get('top_bid_quantity')}"
            )

            log(
                f"  Ask Qty:    "
                f"{option.get('top_ask_quantity')}"
            )

            log(
                f"  Delta:      "
                f"{greeks.get('delta')}"
            )

            log(
                f"  Gamma:      "
                f"{greeks.get('gamma')}"
            )

            log(
                f"  Theta:      "
                f"{greeks.get('theta')}"
            )

            log(
                f"  Vega:       "
                f"{greeks.get('vega')}"
            )


    log("")
    log("==============================================")
    log(" OPTION CHAIN TEST COMPLETE")
    log("==============================================")
    log("READ-ONLY MODE.")
    log("NO ORDERS WERE PLACED.")
    log("NO POSITIONS WERE MODIFIED.")
    log("")


    # --------------------------------------------------
    # Keep worker alive
    # --------------------------------------------------

    while True:

        log(
            "Engine alive: "
            + time.strftime("%Y-%m-%d %H:%M:%S")
        )

        time.sleep(60)


if __name__ == "__main__":
    main()
