import requests
import json

# -----------------------------
# Fill in your credentials
# -----------------------------
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
REDIRECT_URI = "YOUR_REDIRECT_URI"
AUTH_CODE = "AUTHORIZATION_CODE_FROM_OAUTH"

# -----------------------------
# Step 1: Exchange Auth Code for Access Token
# -----------------------------
token_url = "https://wbsapi.withings.net/v2/oauth2"

payload = {
    "action": "requesttoken",
    "grant_type": "authorization_code",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "code": AUTH_CODE,
    "redirect_uri": REDIRECT_URI
}

response = requests.post(token_url, data=payload)
token_data = response.json()

print("Token response:")
print(json.dumps(token_data, indent=2))

access_token = token_data["body"]["access_token"]

# -----------------------------
# Step 2: Fetch Heart Rate Data
# -----------------------------

measure_url = "https://wbsapi.withings.net/measure"

headers = {
    "Authorization": f"Bearer {access_token}"
}

params = {
    "action": "getmeas",
    "meastype": 11,  # 11 = Heart rate
    "category": 1
}

response = requests.post(measure_url, headers=headers, data=params)

print("Heart rate data:")
print(response.json())
