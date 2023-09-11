from flask import (
    Flask,
    redirect,
    render_template,
    url_for,
    session,
    request,
    flash,
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
    flash(
        "You're not authorized to access that page. Please login first.",
        "danger",
    )
    return "authenticated" in session and session["authenticated"]


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        token = sdk.get_oauth_token(username=username, password=password)
        access_token = token.get("access_token")
        if access_token:
            user = sdk.parse_jwt_token(access_token)
            if user:
                session["token"] = access_token
                session["user"] = user
                session["authenticated"] = True
                session["permanent"] = True
                flash("Successfully logged in!", "success")
                return redirect(url_for("index"))
            else:
                flash(
                    "Login unsuccessful. Please check your username and password.",
                    "danger",
                )
                return redirect(url_for("login"))
        else:
            flash(
                "Login unsuccessful. Please check your username and password.", "danger"
            )
            return redirect(url_for("login"))
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


@app.route("/<path:path>")
def catch_all(path):
    if isAuthenticated():
        return redirect(url_for("index"))
    else:
        return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0", debug=True)
