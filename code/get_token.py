import requests
from requests.auth import HTTPBasicAuth

client_id = "xxx"
client_secret = "xxxxxxxx"
redirect_uri = "http://localhost:8000/callback"
code = "xxxxxxxx"

data = {
    "client_id": client_id,
    "grant_type": "authorization_code",
    "redirect_uri": redirect_uri,
    "code": code,
}

response = requests.post(
    "https://api.fitbit.com/oauth2/token",
    data=data,
    auth=HTTPBasicAuth(client_id, client_secret),
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)

print("🔑 Fitbit Token Response:")
print(response.status_code)
print(response.json())




