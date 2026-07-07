#!/usr/bin/env python3
"""SaluteSpeech OAuth helper.

Reads credentials from .env/environment and returns a ready Bearer token.
Supported variables:
  SBER_AUTH_BASIC      Base64 authorization key, without the word Basic
  SBER_CLIENT_ID       Optional alternative to SBER_AUTH_BASIC
  SBER_CLIENT_SECRET   Optional alternative to SBER_AUTH_BASIC
  SBER_SCOPE           Defaults to SALUTE_SPEECH_PERS
  SBER_TOKEN_URL       Defaults to Sber OAuth endpoint
  SBER_SSL_VERIFY      true/false, defaults to true
  SBER_CA_BUNDLE       Optional custom CA bundle path
"""

from __future__ import annotations

import base64
import os
import uuid
from typing import Union

import requests

DEFAULT_TOKEN_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
DEFAULT_SCOPE = "SALUTE_SPEECH_PERS"


def env_bool(name: str, default: bool = True) -> bool:
    raw = os.getenv(name, "").strip().lower()
    if not raw:
        return default
    return raw not in {"0", "false", "no", "off"}


def ssl_verify_setting() -> Union[bool, str]:
    ca_bundle = os.getenv("SBER_CA_BUNDLE", "").strip()
    if ca_bundle:
        return ca_bundle
    return env_bool("SBER_SSL_VERIFY", True)


def build_basic_token() -> str:
    auth_basic = os.getenv("SBER_AUTH_BASIC", "").strip()
    if auth_basic:
        return auth_basic.removeprefix("Basic ").strip()

    client_id = os.getenv("SBER_CLIENT_ID", "").strip()
    client_secret = os.getenv("SBER_CLIENT_SECRET", "").strip()
    if client_id and client_secret:
        raw = f"{client_id}:{client_secret}".encode("utf-8")
        return base64.b64encode(raw).decode("ascii")

    return ""


def get_salute_token(*, verify: Union[bool, str] = True) -> str:
    # Manual token stays supported for quick tests, but auth credentials are preferred.
    manual_token = os.getenv("SBER_SALUTE_TOKEN", "").strip()

    basic_token = build_basic_token()
    if not basic_token:
        if manual_token:
            return manual_token
        raise RuntimeError(
            "Set SBER_AUTH_BASIC or SBER_CLIENT_ID/SBER_CLIENT_SECRET in .env. "
            "Alternatively set SBER_SALUTE_TOKEN manually."
        )

    token_url = os.getenv("SBER_TOKEN_URL", DEFAULT_TOKEN_URL).strip() or DEFAULT_TOKEN_URL
    scope = os.getenv("SBER_SCOPE", DEFAULT_SCOPE).strip() or DEFAULT_SCOPE

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": str(uuid.uuid4()),
        "Authorization": f"Basic {basic_token}",
    }
    response = requests.post(
        token_url,
        headers=headers,
        data={"scope": scope},
        timeout=60,
        verify=verify,
    )

    if response.status_code >= 400:
        raise RuntimeError(f"Sber OAuth error {response.status_code}: {response.text[:1000]}")

    payload = response.json()
    access_token = payload.get("access_token")
    if not access_token:
        raise RuntimeError(f"Sber OAuth response has no access_token: {payload}")

    return str(access_token)


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv(override=True)
    token = get_salute_token(verify=ssl_verify_setting())
    print(f"OK token length: {len(token)}")
