## API Setup Guide

WHOOP uses OAuth2 Authorization Code Flow.  
You must create an application in the WHOOP Developer Dashboard and request user authorization.

---

### Step 1 — Create Developer Application

1. Go to the WHOOP Developer Portal  
   https://developer.whoop.com/

2. Log in with your WHOOP account

3. Open **Developer Dashboard**

4. Create a new application

After creation you will receive:

| Credential | Description |
|------|------|
| Client ID | Public identifier for OAuth |
| Client Secret | Private key (server-side only) |


---

### Step 2 — Configure Redirect URI

In the application settings, register a redirect (callback) URL.

Examples:

| Environment | Redirect URI |
|------|------|
| Local development | http://localhost:8000/whoop/callback |
| Production | https://yourdomain.com/whoop/callback |
| Mobile deep link | whoop://callback |

The redirect URI must match exactly or authentication will fail.

---

### Step 3 — User Authorization

Redirect the user to the WHOOP authorization endpoint:
Link：https://api.prod.whoop.com/oauth/oauth2/auth


Parameters:

| Parameter | Value |
|------|------|
| response_type | code |
| client_id | YOUR_CLIENT_ID |
| redirect_uri | REGISTERED_REDIRECT_URI |
| scope | requested permissions |
| state | random security string |

After login and consent, WHOOP redirects back:
http://localhost:8000/whoop/callback?code=AUTHORIZATION_CODE

### Step 4 — Exchange Code for Token

Send POST request:
https://api.prod.whoop.com/oauth/oauth2/token

Body:

| Field | Value |
|------|------|
| grant_type | authorization_code |
| code | AUTHORIZATION_CODE |
| client_id | YOUR_CLIENT_ID |
| client_secret | YOUR_CLIENT_SECRET |
| redirect_uri | REGISTERED_REDIRECT_URI |

Response:

| Token | Usage |
|------|------|
| access_token | Used for API requests |
| refresh_token | Used to renew access |
| expires_in | Expiration time |

---

### Step 5 — Refresh Token

When the access token expires:
POST https://api.prod.whoop.com/oauth/oauth2/token

grant_type=refresh_token
refresh_token=REFRESH_TOKEN
