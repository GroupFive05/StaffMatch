import json
import os
import time

import requests

_token_cache = {"value": None, "expires_at": 0}


def _credentials() -> dict:
    vcap = json.loads(os.getenv("VCAP_SERVICES", "{}"))
    for instances in vcap.values():
        for inst in instances:
            creds = inst.get("credentials", {})
            if inst.get("label") == "alert-notification" or (
                "client_secret" in creds and "url" in creds and "oauth_url" in creds
            ):
                return creds
    raise RuntimeError("Alert Notification service not bound to this app.")


def _token(creds: dict) -> str:
    if _token_cache["value"] and time.time() < _token_cache["expires_at"] - 30:
        return _token_cache["value"]
    oauth_url = creds["oauth_url"]
    if "/oauth/token" not in oauth_url:
        oauth_url = oauth_url.rstrip("/") + "/oauth/token"
    r = requests.post(
        oauth_url,
        data={"grant_type": "client_credentials"},
        auth=(creds["client_id"], creds["client_secret"]),
        timeout=20,
    )
    r.raise_for_status()
    data = r.json()
    _token_cache["value"] = data["access_token"]
    _token_cache["expires_at"] = time.time() + int(data.get("expires_in", 300))
    return _token_cache["value"]


def send_staffing_request(subject: str, body: str) -> None:
    creds = _credentials()
    event = {
        "eventType": "StaffingRequest",
        "resource": {"resourceName": "StaffMatch", "resourceType": "application"},
        "severity": "INFO",
        "category": "NOTIFICATION",
        "subject": subject,
        "body": body,
    }
    r = requests.post(
        creds["url"].rstrip("/") + "/cf/producer/v1/resource-events",
        json=event,
        headers={"Authorization": f"Bearer {_token(creds)}"},
        timeout=20,
    )
    r.raise_for_status()
