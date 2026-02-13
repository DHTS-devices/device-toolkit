import time
import webbrowser
import urllib.parse
import requests
import pandas as pd

# -----------------------------
# 0) Fill these from Withings Developer Dashboard
# -----------------------------
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
REDIRECT_URI = "https://example.com/callback"  # must match the one you registered
STATE = "random_state_string"

# Needed scope for blood pressure measurements
SCOPE = "user.metrics"  # for Measure - Getmeas :contentReference[oaicite:3]{index=3}

# Endpoints
AUTH_URL = "https://account.withings.com/oauth2_user/authorize2"  # :contentReference[oaicite:4]{index=4}
TOKEN_URL = "https://wbsapi.withings.net/v2/oauth2"               # :contentReference[oaicite:5]{index=5}
MEASURE_URL = "https://wbsapi.withings.net/measure"               # Measure - Getmeas

# Measurement type codes (Withings)
MEASTYPE_DIA = 9   # diastolic (mmHg) :contentReference[oaicite:6]{index=6}
MEASTYPE_SYS = 10  # systolic (mmHg)  :contentReference[oaicite:7]{index=7}
MEASTYPE_HR  = 11  # heart pulse (bpm) :contentReference[oaicite:8]{index=8}


def build_authorize_url():
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "state": STATE,
    }
    return f"{AUTH_URL}?{urllib.parse.urlencode(params)}"


def exchange_code_for_tokens(code: str) -> dict:
    """
    Exchange authorization code for access_token + refresh_token.
    """
    data = {
        "action": "requesttoken",
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    r = requests.post(TOKEN_URL, data=data, timeout=30)
    r.raise_for_status()
    payload = r.json()
    if payload.get("status") != 0:
        raise RuntimeError(f"Token exchange failed: {payload}")
    return payload["body"]  # contains access_token, refresh_token, userid, expires_in


def refresh_access_token(refresh_token: str) -> dict:
    """
    Refresh access_token using refresh_token.
    """
    data = {
        "action": "requesttoken",
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
    }
    r = requests.post(TOKEN_URL, data=data, timeout=30)
    r.raise_for_status()
    payload = r.json()
    if payload.get("status") != 0:
        raise RuntimeError(f"Token refresh failed: {payload}")
    return payload["body"]


def get_bp_hr_measurements(access_token: str, start_ts: int, end_ts: int) -> dict:
    """
    Fetch blood pressure + heart pulse measurements.
    Withings uses form-encoded POST for many endpoints.
    """
    data = {
        "action": "getmeas",
        "access_token": access_token,
        "meastypes": f"{MEASTYPE_DIA},{MEASTYPE_SYS},{MEASTYPE_HR}",
        "category": 1,  # 1 = real measurement
        "startdate": start_ts,
        "enddate": end_ts,
    }
    r = requests.post(MEASURE_URL, data=data, timeout=30)
    r.raise_for_status()
    payload = r.json()
    if payload.get("status") != 0:
        raise RuntimeError(f"Getmeas failed: {payload}")
    return payload["body"]


def parse_measure_groups_to_rows(body: dict) -> pd.DataFrame:
    """
    Convert Withings 'measuregrps' into a flat table.

    Each 'measuregrp' usually corresponds to one measurement session
    (same timestamp), containing multiple measures (SYS/DIA/HR).
    """
    rows = []
    for grp in body.get("measuregrps", []):
        dt = grp.get("date")  # unix timestamp
        measures = grp.get("measures", [])
        row = {"timestamp": pd.to_datetime(dt, unit="s")}
        for m in measures:
            t = m.get("type")
            value = m.get("value")
            unit_pow = m.get("unit", 0)  # value * 10^unit
            real_val = value * (10 ** unit_pow)

            if t == MEASTYPE_SYS:
                row["systolic_mmhg"] = real_val
            elif t == MEASTYPE_DIA:
                row["diastolic_mmhg"] = real_val
            elif t == MEASTYPE_HR:
                row["heart_rate_bpm"] = real_val

        # keep only rows that have at least BP
        if "systolic_mmhg" in row or "diastolic_mmhg" in row:
            rows.append(row)

    df = pd.DataFrame(rows).sort_values("timestamp").reset_index(drop=True)
    return df


if __name__ == "__main__":
    # 1) Ask user to authorize in browser (OAuth web flow) :contentReference[oaicite:9]{index=9}
    auth = build_authorize_url()
    print("Open this URL in your browser and authorize:")
    print(auth)
    try:
        webbrowser.open(auth)
    except Exception:
        pass

    # 2) Paste the redirected URL you land on (it contains ?code=...)
    redirected_url = input("\nPaste the FULL redirected URL here:\n> ").strip()
    qs = urllib.parse.parse_qs(urllib.parse.urlparse(redirected_url).query)

    code = qs.get("code", [None])[0]
    state = qs.get("state", [None])[0]
    if not code:
        raise SystemExit("No code found in redirected URL.")
    if state != STATE:
        raise SystemExit("State mismatch. Abort for safety.")

    # 3) Exchange code for tokens
    tokens = exchange_code_for_tokens(code)
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    userid = tokens.get("userid")
    expires_in = tokens.get("expires_in")
    print(f"\nGot tokens for userid={userid}, expires_in={expires_in}s")

    # 4) Fetch last 30 days of BP/HR
    end_ts = int(time.time())
    start_ts = end_ts - 30 * 24 * 3600

    body = get_bp_hr_measurements(access_token, start_ts, end_ts)
    df = parse_measure_groups_to_rows(body)

    print("\nSample:")
    print(df.head(10))

    # 5) Save to CSV
    out = "withings_bpmconnect_bp_hr_last30days.csv"
    df.to_csv(out, index=False)
    print(f"\nSaved: {out}")
