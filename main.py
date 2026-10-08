import os
import time
from datetime import date

from dhanhq import DhanContext, dhanhq


# ============================================================
# NIFTY INTELLIGENCE ENGINE
# VERSION 0.2
# OPTION CHAIN DATA TEST
# ============================================================


def log(message=""):
    print(message, flush=True)


def safe_number(value, default=0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def main():

    log("==============================================")
    log(" NIFTY INTELLIGENCE ENGINE v0.2")
    log(" DHAN OPTION CHAIN TEST")
    log("==============================================")

    # --------------------------------------------------------
    # 1. Load credentials
    # --------------------------------------------------------

    client_id = os.getenv("DHAN_CLIENT_ID")
    access_token = os.getenv("DHAN_ACCESS_TOKEN")

    if not client_id:
        raise RuntimeError("DHAN_CLIENT_ID is missing.")

    if not access_token:
        raise RuntimeError("DHAN_ACCESS_TOKEN is missing.")

    log("Credentials found.")
    log(f"Client ID: {client_id[:4]}****")
    log("")


    # --------------------------------------------------------
    # 2. Create Dhan connection
    # --------------------------------------------------------

    log("Creating DhanContext...")

    dhan_context = DhanContext(
        client_id,
        access_token
    )

    dhan = dhanhq(dhan_context)

    log("DhanHQ client initialized.")
    log("")


    # --------------------------------------------------------
    # 3. NIFTY configuration
    # --------------------------------------------------------

    # Dhan Security ID for NIFTY index
    NIFTY_SECURITY_ID = 13

    # Dhan exchange segment for index instruments
    NIFTY_SEGMENT = dhan.INDEX

    log("NIFTY configuration:")
    log(f"Security ID: {NIFTY_SECURITY_ID}")
    log(f"Segment: {NIFTY_SEGMENT}")
    log("")


    # --------------------------------------------------------
    # 4. Get available NIFTY expiries
    # --------------------------------------------------------

    log("Requesting NIFTY expiry list...")

    try:

        expiry_response = dhan.expiry_list(
            NIFTY_SECURITY_ID,
            NIFTY_SEGMENT
        )

    except Exception as error:

        log("==============================================")
        log(" EXPIRY LIST REQUEST FAILED")
        log("==============================================")
        log(f"Error type: {type(error).__name__}")
        log(f"Error: {error}")
        raise


    if not isinstance(expiry_response, dict):
        raise RuntimeError(
            "Unexpected expiry-list response format."
        )


    if expiry_response.get("status") != "success":
        raise RuntimeError(
            f"Expiry list failed: {expiry_response}"
        )


    expiries = expiry_response.get("data", [])


    if not expiries:
        raise RuntimeError(
            "Dhan returned no active NIFTY expiries."
        )


    log("")
    log("Available NIFTY expiries:")

    for expiry in expiries[:10]:
        log(f"  {expiry}")


    # --------------------------------------------------------
    # 5. Select nearest active expiry
    # --------------------------------------------------------

    today = date.today()

    valid_expiries = []

    for expiry in expiries:

        try:
            expiry_date = date.fromisoformat(expiry)

            if expiry_date >= today:
                valid_expiries.append(expiry)

        except ValueError:
            continue


    if not valid_expiries:
        raise RuntimeError(
            "Could not find a valid future NIFTY expiry."
        )


    selected_expiry = valid_expiries[0]

    log("")
    log(f"Selected nearest expiry: {selected_expiry}")


    # --------------------------------------------------------
    # 6. Request complete option chain
    # --------------------------------------------------------

    log("")
    log("Requesting NIFTY option chain...")
    log("")

    try:

        option_response = dhan.option_chain(
            NIFTY_SECURITY_ID,
            NIFTY_SEGMENT,
            selected_expiry
        )

    except Exception as error:

        log("==============================================")
        log(" OPTION CHAIN REQUEST FAILED")
        log("==============================================")
        log(f"Error type: {type(error).__name__}")
        log(f"Error: {error}")
        raise


    if not isinstance(option_response, dict):
        raise RuntimeError(
            "Unexpected option-chain response format."
        )


    if option_response.get("status") != "success":
        raise RuntimeError(
            f"Option chain failed: {option_response}"
        )


    data = option_response.get("data", {})

    underlying_price = safe_number(
        data.get("last_price")
    )

    option_chain = data.get("oc", {})


    if not option_chain:
        raise RuntimeError(
            "Option chain returned no strike data."
        )


    log("==============================================")
    log(" OPTION CHAIN RECEIVED SUCCESSFULLY")
    log("==============================================")

    log(f"NIFTY LTP: {underlying_price:.2f}")
    log(f"Expiry: {selected_expiry}")
    log(f"Number of strikes received: {len(option_chain)}")
    log("")


    # --------------------------------------------------------
    # 7. Find ATM strike
    # --------------------------------------------------------

    strikes = []

    for strike in option_chain.keys():

        try:
            strikes.append(float(strike))
        except (TypeError, ValueError):
            continue


    if not strikes:
        raise RuntimeError(
            "Could not identify strikes in option chain."
        )


    atm_strike = min(
        strikes,
        key=lambda strike: abs(strike - underlying_price)
    )


    log(f"ATM strike: {atm_strike:.2f}")
    log("")


    # --------------------------------------------------------
    # 8. Select ATM +/- 5 strikes
    # --------------------------------------------------------

    sorted_strikes = sorted(strikes)

    atm_index = sorted_strikes.index(atm_strike)

    start_index = max(0, atm_index - 5)
    end_index = min(
        len(sorted_strikes),
        atm_index + 6
    )

    selected_strikes = sorted_strikes[
        start_index:end_index
    ]


    # --------------------------------------------------------
    # 9. Print option data
    # --------------------------------------------------------

    log("==============================================================")
    log(" NIFTY OPTION CHAIN — ATM +/- 5")
    log("==============================================================")

    header = (
        f"{'STRIKE':>8} | "
        f"{'CE LTP':>8} | "
        f"{'CE OI':>12} | "
        f"{'CE ΔOI':>12} | "
        f"{'CE IV':>7} | "
        f"{'PE LTP':>8} | "
        f"{'PE OI':>12} | "
        f"{'PE ΔOI':>12} | "
        f"{'PE IV':>7}"
    )

    log(header)

    log("-" * len(header))


    for strike in selected_strikes:

        strike_key = str(strike)

        # Dhan normally returns strike keys as decimal strings.
        # Try alternate formatting if required.
        strike_data = option_chain.get(strike_key)

        if strike_data is None:
            strike_data = option_chain.get(
                f"{strike:.6f}"
            )

        if strike_data is None:
            continue


        ce = strike_data.get("ce", {})
        pe = strike_data.get("pe", {})


        ce_ltp = safe_number(
            ce.get("last_price")
        )

        ce_oi = safe_number(
            ce.get("oi")
        )

        ce_prev_oi = safe_number(
            ce.get("previous_oi")
        )

        ce_doi = ce_oi - ce_prev_oi

        ce_iv = safe_number(
            ce.get("implied_volatility")
        )


        pe_ltp = safe_number(
            pe.get("last_price")
        )

        pe_oi = safe_number(
            pe.get("oi")
        )

        pe_prev_oi = safe_number(
            pe.get("previous_oi")
        )

        pe_doi = pe_oi - pe_prev_oi

        pe_iv = safe_number(
            pe.get("implied_volatility")
        )


        log(
            f"{strike:8.0f} | "
            f"{ce_ltp:8.2f} | "
            f"{ce_oi:12,.0f} | "
            f"{ce_doi:12,.0f} | "
            f"{ce_iv:7.2f} | "
            f"{pe_ltp:8.2f} | "
            f"{pe_oi:12,.0f} | "
            f"{pe_doi:12,.0f} | "
            f"{pe_iv:7.2f}"
        )


    # --------------------------------------------------------
    # 10. Display detailed ATM information
    # --------------------------------------------------------

    atm_data = option_chain.get(
        str(atm_strike)
    )

    if atm_data is None:
        atm_data = option_chain.get(
            f"{atm_strike:.6f}"
        )


    log("")
    log("==============================================================")
    log(" ATM DETAILED DATA")
    log("==============================================================")


    if atm_data:

        for option_type in ["ce", "pe"]:

            option = atm_data.get(option_type, {})

            if not option:
                continue

            label = "CALL" if option_type == "ce" else "PUT"

            greeks = option.get("greeks", {})

            log("")
            log(f"{label}")
            log(f"  LTP:        {option.get('last_price')}")
            log(f"  OI:         {option.get('oi')}")
            log(f"  Previous OI:{option.get('previous_oi')}")
            log(f"  Volume:     {option.get('volume')}")
            log(f"  IV:         {option.get('implied_volatility')}")
            log(f"  Bid:        {option.get('top_bid_price')}")
            log(f"  Ask:        {option.get('top_ask_price')}")
            log(f"  Bid Qty:    {option.get('top_bid_quantity')}")
            log(f"  Ask Qty:    {option.get('top_ask_quantity')}")
            log(f"  Delta:      {greeks.get('delta')}")
            log(f"  Gamma:      {greeks.get('gamma')}")
            log(f"  Theta:      {greeks.get('theta')}")
            log(f"  Vega:       {greeks.get('vega')}")


    log("")
    log("==============================================================")
    log(" OPTION CHAIN TEST COMPLETE")
    log("==============================================================")
    log("READ-ONLY MODE.")
    log("NO ORDERS WERE PLACED.")
    log("NO POSITIONS WERE MODIFIED.")
    log("")


    # --------------------------------------------------------
    # 11. Keep Render worker alive
    # --------------------------------------------------------

    while True:

        log(
            "Engine alive: "
            + time.strftime("%Y-%m-%d %H:%M:%S")
        )

        time.sleep(60)


if __name__ == "__main__":
    main()
