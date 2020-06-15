import hmac
import random
import requests
import collections
from flask import Flask, request, abort, render_template, redirect

from lib import (
    hook,
    hooks,
    get_digest,
    get_badges,
    format_event,
    post_badge_checkedin,
    API_ACCESS_KEY,
)

app = Flask(__name__)

# Retrieve the current badges from the API.
badges = get_badges()
prints = []


@app.route("/")
def index():
    """
    Render a dashboard with current data. Optional.
    """

    return render_template("app.html", prints=prints, badges=badges)


@app.route("/<badge>/<privilege>", methods=["POST"])
def badge_checkedin(badge, privilege):
    """
    Route used by dashboard for manual checking in of badges.
    """

    post_badge_checkedin(badge, privilege, None)

    return redirect("/")


@app.route("/", methods=["POST"])
def post_receive():
    """
    Webhook receiving route.
    """

    digest = get_digest()

    if digest and (
        not "X-Accredion-Signature" in request.headers
        or not hmac.compare_digest(request.headers["X-Accredion-Signature"], digest)
    ):
        abort(400, "Invalid signature")

    data = request.json
    type = request.json["meta"]["type"]

    app.logger.info(
        "%s (%s)", format_event(type, data), request.headers["X-Accredion-Delivery"]
    )

    for hook in hooks.get(type, []):
        hook(data)

    return ""


@hook("badges")
def on_badges(data):
    """
    Handler for the "badges" events.
    """

    id = data["data"]["id"]
    badge = data["data"]

    event = data["meta"]["event"]

    if event == "created":
        # Append if the action is created
        badges.append(badge)
    else:
        # Otherwise update
        i = next(i for i, b in enumerate(badges) if b["id"] == badge["id"])
        badges[i] = badge


@hook("prints")
def on_prints(data):
    """
    Handler for the "prints" events.
    """

    printjob = data["data"]

    prints.append(printjob)

    badge_id = printjob["relationships"]["badge"]["data"]["id"]
    # Lookup the badge from the included section.
    badge = next(filter(lambda x: x["id"] == badge_id, data["included"]))

    result = do_print(printjob, badge)

    i = prints.index(printjob)

    if result == 0:
        prints[i]["attributes"]["status"] = "complete"
        r = requests.post(
            printjob["links"]["complete"],
            headers={"Authentication": "Bearer {}".format(API_ACCESS_KEY)},
        )
    else:
        prints[i]["attributes"]["status"] = "fail"
        r = requests.post(
            printjob["links"]["fail"],
            json={"code": result},
            headers={"Authentication": "Bearer {}".format(API_ACCESS_KEY)},
        )


def do_print(print, badge):
    # This should perform the actual print.
    return random.randint(0, 1)


if __name__ == "__main__":
    app.run()
