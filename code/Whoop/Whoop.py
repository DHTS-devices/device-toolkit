"""
whoop_oauth_demo.py

A minimal FastAPI demo for WHOOP OAuth2 (Authorization Code) + calling WHOOP API.

What you get:
- /login    -> redirect user to WHOOP authorization page
- /callback -> receives ?code=..., exchanges it for access/refresh token, stores in SQLite
- /me       -> example API call (basic profile)
- /recovery -> example API call (recovery endpoint)

Setup:
1) pip install fastapi uvicorn httpx python-dotenv
2) Create a .env file (same folder) with:
   WHOOP_CLIENT_ID=xxxx
   WHOOP_CLIENT_SECRET=xxxx
   WHOOP_REDIRECT_URI=http://localhost:8000/callback
   WHOOP_SCOPES=read:profile read:recovery read:sleep read:workout read:cycle
3) Run:
   uvicorn whoop_oauth_demo:app --reload --port 8000
4) Open:
   http://localhost:8000/login

Notes:
- Client Secret must stay server-side.
- This demo stores tokens in a local SQLite file: whoop_tokens.sqlite
- WHOOP base URLs (per docs):
  Auth:  https://api.prod.whoop.com/oauth/oauth2/auth
  Token: https://api.prod.whoop.com/oauth/oauth2/token
  API:   https://api.prod.whoop.com/developer
"""

from __future__ import annotations

import os
import secrets
import sqlite3
import time
from typing import Any, Dict, Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse

load_dotenv()

WHOOP_CLIENT_ID = os.getenv("WHOOP_CLIENT_ID", "").strip()
WHOOP_CLIENT_SECRET = os.getenv("WHOOP_CLIENT_SECRET", "").strip()
WHOOP_REDIRECT_URI = os.getenv("WHOOP_REDIRECT_URI", "http://localhost:8000/callback").strip()
WHOOP_SCOPES = os.getenv("WHOOP_SCOPES", "read:profile").strip()

WHOOP_AUTH_URL = "https://api.prod.whoop.com/oauth/oauth2/auth"
WHOOP_TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"

# WHOOP API base for developer endpoints
WHOOP_API_BASE = "https://api.prod.whoop.com/developer"

DB_PATH = os.getenv("WHOOP_TOKEN_DB", "whoop_tokens.sqlite")

app = FastAPI(title="WHOOP OAuth Demo")


# --------------------------
# SQLite: tiny token store
# --------------------------
def db_init() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tokens (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                access_token TEXT,
                refresh_token TEXT,
                expires_at INTEGER
            )
            """
        )
        conn.execute("INSERT OR IGNORE INTO tokens (id, access_token, refresh_token, expires_at) VALUES (1, '', '', 0)")
        conn.commit()


def db_get_tokens() -> Dict[str, Any]:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT access_token, refresh_token, expires_at FROM tokens WHERE id = 1").fetchone()
        if not row:
            return {"access_token": "", "refresh_token": "", "expires_at": 0}
        return {"access_token": row[0] or "", "refresh_token": row[1] or "", "expires_at": int(row[2] or 0)}


def db_save_tokens(access_token: str, refresh_token: str, expires_in: int) -> None:
    # expires_in is seconds from now
    expires_at = int(time.time()) + int(expires_in) - 30  # small safety buffer
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE tokens SET access_token = ?, refresh_token = ?, expires_at = ? WHERE id = 1",
            (access_token, refresh_token, expires_at),
        )
        conn.commit()


db_init()


# --------------------------
# Helpers
# --------------------------
def require_env() -> None:
    missing = []
    if not WHOOP_CLIENT_ID:
        missing.append("WHOOP_CLIENT_ID")
    if not WHOOP_CLIENT_SECRET:
        missing.append("WHOOP_CLIENT_SECRET")
    if not WHOOP_REDIRECT_URI:
        missing.append("WHOOP_REDIRECT_URI")
    if missing:
        raise HTTPException(
            status_code=500,
            detail=f"Missing env vars: {', '.join(missing)}. Please set them in .env.",
        )


async def whoop_token_exchange(code: str) -> Dict[str, Any]:
    require_env()
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": WHOOP_CLIENT_ID,
        "client_secret": WHOOP_CLIENT_SECRET,
        "redirect_uri": WHOOP_REDIRECT_URI,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(WHOOP_TOKEN_URL, data=data)
        if resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=f"Token exchange failed: {resp.text}")
        return resp.json()


async def whoop_refresh(refresh_token: str) -> Dict[str, Any]:
    require_env()
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": WHOOP_CLIENT_ID,
        "client_secret": WHOOP_CLIENT_SECRET,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(WHOOP_TOKEN_URL, data=data)
        if resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=f"Token refresh failed: {resp.text}")
        return resp.json()


async def get_valid_access_token() -> str:
    t = db_get_tokens()
    if not t["access_token"] or not t["refresh_token"]:
        raise HTTPException(status_code=401, detail="No tokens stored yet. Visit /login first.")
    if int(time.time()) < int(t["expires_at"]):
        return t["access_token"]

    # refresh
    refreshed = await whoop_refresh(t["refresh_token"])
    access_token = refreshed.get("access_token", "")
    refresh_token = refreshed.get("refresh_token", t["refresh_token"])  # some providers rotate; keep old if missing
    expires_in = int(refreshed.get("expires_in", 3600))
    if not access_token:
        raise HTTPException(status_code=401, detail="Refresh did not return access_token.")
    db_save_tokens(access_token, refresh_token, expires_in)
    return access_token


async def whoop_get(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    token = await get_valid_access_token()
    url = f"{WHOOP_API_BASE}{path}"
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url, headers=headers, params=params)
        if resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=f"WHOOP API error: {resp.text}")
        return resp.json()


# --------------------------
# Routes
# --------------------------
@app.get("/")
async def root():
    return {
        "ok": True,
        "routes": ["/login", "/callback", "/me", "/recovery"],
        "next": "Open /login to authorize a WHOOP user.",
    }


@app.get("/login")
async def login(request: Request):
    """
    Redirect user to WHOOP auth page.
    """
    require_env()

    # state is recommended to prevent CSRF; store it in a cookie for this demo
    state = secrets.token_urlsafe(24)

    # WHOOP expects scopes space-separated
    scope = WHOOP_SCOPES

    auth_url = (
        f"{WHOOP_AUTH_URL}"
        f"?response_type=code"
        f"&client_id={httpx.URL('').copy_with(query={'v': WHOOP_CLIENT_ID}).params['v']}"
        f"&redirect_uri={httpx.URL('').copy_with(query={'v': WHOOP_REDIRECT_URI}).params['v']}"
        f"&scope={httpx.URL('').copy_with(query={'v': scope}).params['v']}"
        f"&state={httpx.URL('').copy_with(query={'v': state}).params['v']}"
    )

    resp = RedirectResponse(url=auth_url, status_code=302)
    resp.set_cookie("whoop_oauth_state", state, httponly=True, samesite="lax")
    return resp


@app.get("/callback")
async def callback(request: Request, code: str = "", state: str = ""):
    """
    WHOOP redirects here with ?code=...&state=...
    """
    require_env()

    cookie_state = request.cookies.get("whoop_oauth_state", "")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code in callback.")
    if not state or not cookie_state or state != cookie_state:
        raise HTTPException(status_code=400, detail="State mismatch. Please restart auth via /login.")

    token_json = await whoop_token_exchange(code)

    access_token = token_json.get("access_token", "")
    refresh_token = token_json.get("refresh_token", "")
    expires_in = int(token_json.get("expires_in", 3600))

    if not access_token or not refresh_token:
        raise HTTPException(status_code=500, detail=f"Token response missing fields: {token_json}")

    db_save_tokens(access_token, refresh_token, expires_in)

    return JSONResponse(
        {
            "ok": True,
            "stored": True,
            "expires_in": expires_in,
            "next": ["GET /me", "GET /recovery"],
        }
    )


@app.get("/me")
async def me():
    """
    Example: fetch basic user profile.
    """
    # Path names can differ by API version; adjust if your endpoint differs in WHOOP docs.
    # Common example in WHOOP docs: /v1/user/profile/basic
    return await whoop_get("/v1/user/profile/basic")


@app.get("/recovery")
async def recovery(limit: int = 7):
    """
    Example: fetch recovery records (recent).
    """
    # Common example in WHOOP docs: /v1/recovery
    # You may need date ranges depending on the endpoint behavior.
    data = await whoop_get("/v1/recovery")
    # If API returns a list, optionally truncate for convenience
    if isinstance(data, dict) and "records" in data and isinstance(data["records"], list):
        data["records"] = data["records"][: max(1, min(limit, 30))]
    return data
