import requests
from requests.auth import HTTPBasicAuth
from datetime import date
import csv
import json
import matplotlib.pyplot as plt

client_id = "xxx"
client_secret = "xxxxxxx"
redirect_uri = "http://localhost:8000/callback"
code = "xxxxxxx"

def fetch_token():
    token_url = "https://api.fitbit.com/oauth2/token"
    data = {
        "client_id": client_id,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
        "code": code,
    }
    response = requests.post(
        token_url,
        data=data,
        auth=HTTPBasicAuth(client_id, client_secret),
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print("\n Token Response:")
    print(response.status_code)
    print(response.json())
    return response.json()

def fetch_today_data(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    today = date.today().isoformat()

    endpoints = {
        "activity": f"https://api.fitbit.com/1/user/-/activities/date/{today}.json",
        "heartrate": f"https://api.fitbit.com/1/user/-/activities/heart/date/{today}/1d/1min.json",
        "sleep": f"https://api.fitbit.com/1.2/user/-/sleep/date/{today}.json",
        "profile": "https://api.fitbit.com/1/user/-/profile.json"
    }

    all_data = {}
    for key, url in endpoints.items():
        print(f"\n Fetching {key}...")
        res = requests.get(url, headers=headers)
        print(res.status_code)
        json_data = res.json()
        print(json_data)
        all_data[key] = json_data

    with open("fitbit_today_data.json", "w") as jf:
        json.dump(all_data, jf, indent=2)

    with open("fitbit_summary.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value"])
        summary = all_data['activity'].get("summary", {})
        for key, value in summary.items():
            if isinstance(value, (int, float)):
                writer.writerow([key, value])

    return all_data

def plot_from_csv():
    import pandas as pd

    df = pd.read_csv("fitbit_summary.csv")
    df.set_index("metric", inplace=True)
    df.plot(kind="bar", legend=False)
    plt.title("Today's Fitbit Summary")
    plt.ylabel("Value")
    plt.tight_layout()
    plt.savefig("fitbit_summary_plot.png")
    plt.show()

if __name__ == "__main__":
    token_response = fetch_token()
    if "access_token" in token_response:
        fetch_today_data(token_response["access_token"])
        plot_from_csv()
    else:
        print(" Get access_token error，please check code and secret if all good")
