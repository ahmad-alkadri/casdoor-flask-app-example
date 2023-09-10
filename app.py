from flask import (
    Flask,
    redirect,
    render_template,
    url_for,
    session,
    request,
)
from casdoor import CasdoorSDK
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("APPLICATION_CLIENTSECRET")
app.config["SESSION_TYPE"] = "filesystem"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=3)

from flask_session import Session

Session(app)

# The `authCfg` dictionary is used to store the authentication configuration
# for the Casdoor SDK. It contains the following key-value pairs:
authCfg = {
    "endpoint": os.getenv("CASSDOOR_ENDPOINT"),
    "client_id": os.getenv("APPLICATION_CLIENTID"),
    "client_secret": os.getenv("APPLICATION_CLIENTSECRET"),
    "certificate": os.getenv("APPLICATION_CERTIFICATE").replace("\\n", "\n"),
    "org_name": os.getenv("APPLICATION_ORGNAME"),
    "application_name": os.getenv("APPLICATION_NAME"),
}


sdk = CasdoorSDK(**authCfg)


def isAuthenticated():
    return "authenticated" in session and session["authenticated"]


@app.route("/login")
def login():
    if isAuthenticated():
        return redirect(url_for("index"))
    else:
        return render_template("login.html")


@app.route("/")
def index():
    if isAuthenticated():
        return redirect(url_for("home"))
    else:
        return redirect(url_for("login"))


@app.route("/home")
def home():
    if isAuthenticated():
        return render_template("home.html")
    else:
        return redirect(url_for("login"))


@app.route("/login/redirect")
def initiate_login():
    if isAuthenticated():
        return redirect(url_for("index"))
    else:
        authorizationEndpoint = f"{authCfg['endpoint']}/login/oauth/authorize"
        params = {
            "client_id": authCfg["client_id"],
            "redirect_uri": os.getenv("APPLICATION_CALLBACK"),
            "response_type": "code",
            "scope": "read",
        }
        casdoorUrl = f"{authorizationEndpoint}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        return redirect(casdoorUrl)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/profile")
def profile():
    if isAuthenticated():
        user_info = session.get("user")
        return render_template("profile.html", user=user_info)
    else:
        return redirect(url_for("login"))


@app.route("/callback")
def callback():
    if isAuthenticated():
        return redirect(url_for("index"))
    else:
        code = request.args.get("code")
        token = sdk.get_oauth_token(code=code)
        access_token = token.get("access_token")
        user = sdk.parse_jwt_token(access_token)
        if user:
            session["token"] = access_token
            session["user"] = user
            session["authenticated"] = True
            session["permanent"] = True
            return redirect(url_for("index"))
        else:
            return redirect(url_for("login"))


@app.route("/<path:path>")
def catch_all(path):
    if isAuthenticated():
        return redirect(url_for("index"))
    else:
        return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0", debug=True)
