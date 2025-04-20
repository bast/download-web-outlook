from flask import Flask, redirect, request, session, url_for
from flask_session import Session
import requests
import uuid


from config import APP_SECRET_KEY, CLIENT_ID, CLIENT_SECRET, AUTHORITY, REDIRECT_URI


app = Flask(__name__)
app.secret_key = APP_SECRET_KEY
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def home():
    # Case 1: Returning from Microsoft with a code
    if "code" in request.args:
        if request.args.get("state") != session.get("state"):
            return "State mismatch. Possible CSRF attack.", 400

        code = request.args.get("code")
        token_url = f"{AUTHORITY}/oauth2/v2.0/token"
        data = {
            "client_id": CLIENT_ID,
            "scope": "Mail.Read",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
            "client_secret": CLIENT_SECRET,
        }

        token_res = requests.post(token_url, data=data)
        token_json = token_res.json()

        if "access_token" not in token_json:
            return f"Error getting token: {token_json}"

        session["access_token"] = token_json["access_token"]
        return redirect(url_for("emails"))

    # Case 2: Normal visit - show login link
    return '<a href="/login">Login with Microsoft</a>'


@app.route("/login")
def login():
    state = str(uuid.uuid4())
    session["state"] = state

    auth_url = (
        f"{AUTHORITY}/oauth2/v2.0/authorize?"
        f"response_type=code&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=Mail.Read&state={state}"
    )
    return redirect(auth_url)


def run():
    # extract port from REDIRECT_URI
    port = REDIRECT_URI.split(":")[-1]

    app.run(port=port, debug=True)
