import os
import hmac
import hashlib
import requests
import collections
from flask import request, abort

API_HOST = os.environ.get("API_HOST", "https://ebu.staging.accredion.com")
API_PATH = "/api/riedel/v1"
API_ACCESS_KEY = os.environ.get("API_ACCESS_KEY")

API_ROOT = API_HOST + API_PATH

SECRET = os.environ.get("SECRET")
EVENT_ID = os.environ.get("EVENT_ID")

hooks = collections.defaultdict(list)


def get_badges():
    return (
        requests.get(
            "{}/events/{event}/badges".format(API_ROOT, event=EVENT_ID),
            headers={"Authentication": "Bearer {}".format(API_ACCESS_KEY)},
        ).json()["data"]
        if EVENT_ID
        else []
    )


def post_badge_checkedin(badge_id, privilege_id, event):
    return requests.post(
        "{}/badges/{badge}/checkedin".format(API_ROOT, badge=badge_id),
        json={"privilegeId": privilege_id, "event": event},
        headers={"Authentication": "Bearer {}".format(API_ACCESS_KEY)},
    )


def hook(event_type="push"):
    def decorator(func):
        hooks[event_type].append(func)
        return func

    return decorator


def get_digest():
    return (
        hmac.new(SECRET.encode("utf-8"), request.data, hashlib.sha1).hexdigest()
        if SECRET
        else None
    )


def format_event(type, data):
    return EVENT_DESCRIPTIONS[type].format(**data)


EVENT_DESCRIPTIONS = {
    "badges": "{meta[event]} badge {data[id]}",
    "prints": "{meta[event]} print {data[id]}",
}
