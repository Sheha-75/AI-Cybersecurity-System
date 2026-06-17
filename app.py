from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for
)

import pandas as pd
import pyotp

from auth_system import (
    main_ai,
    ai_auditor,
    detect_replay
)

from otp_config import SECRET

app = Flask(__name__)

# Change this to a long random value before deployment
app.secret_key = "ai-cyber-project-super-secret-key-2026"


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    typing_time = float(
        request.form.get("typing_time", 0)
    )

    print(
        f"Browser typing time: {typing_time:.2f}"
    )

    replay = detect_replay(
        username,
        password,
        typing_time
    )

    if replay:

        return render_template(
            "result.html",
            message="🚨 Replay Attack Detected",
            risk_score=100
        )

    decision, risk_score = main_ai(
        username,
        password,
        typing_time,
        replay=replay
    )

    audit = ai_auditor(
        decision,
        typing_time
    )

    # High-risk suspicious behavior
    if audit == "FLAGGED":

        return render_template(
            "result.html",
            message="❌ Access Denied (Suspicious Behavior)",
            risk_score=risk_score
        )

    # Low risk → direct access
    if decision == "ALLOW" and risk_score <= 30:

        session["authenticated"] = True
        session["username"] = username

        return render_template(
            "result.html",
            message="✅ Access Granted",
            risk_score=risk_score
        )

    # Medium risk → OTP required
    elif decision == "ALLOW" and risk_score <= 70:

        session["pending_user"] = username
        session["pending_risk"] = risk_score

        return redirect(url_for("otp"))

    # High risk → deny
    return render_template(
        "result.html",
        message="❌ Access Denied",
        risk_score=risk_score
    )


@app.route("/otp")
def otp():

    if "pending_user" not in session:
        return redirect(url_for("home"))

    return render_template("otp.html")


@app.route("/verify-otp", methods=["POST"])
def verify_otp():

    if "pending_user" not in session:
        return redirect(url_for("home"))

    code = request.form["otp"]

    totp = pyotp.TOTP(SECRET)

    if totp.verify(code):

        session["authenticated"] = True
        session["username"] = session["pending_user"]

        risk_score = session.get("pending_risk", 50)

        session.pop("pending_user", None)
        session.pop("pending_risk", None)

        return render_template(
            "result.html",
            message="✅ Access Granted (OTP Verified)",
            risk_score=risk_score
        )

    return render_template(
        "result.html",
        message="❌ Invalid OTP",
        risk_score=100
    )


@app.route("/admin")
def admin():

    if not session.get("authenticated"):
        return redirect(url_for("home"))

    try:
        df = pd.read_csv("security_logs.csv")

        total_attempts = len(df)

        successful = len(
            df[df["decision"] == "ALLOW"]
        )

        denied = len(
            df[df["decision"] == "DENY"]
        )

        attack_counts = (
            df["attack_type"]
            .value_counts()
            .to_dict()
        )

        recent_logs = (
            df.tail(10)
            .to_dict(orient="records")
        )

    except Exception:

        total_attempts = 0
        successful = 0
        denied = 0
        attack_counts = {}
        recent_logs = []

    return render_template(
        "admin.html",
        total_attempts=total_attempts,
        successful=successful,
        denied=denied,
        attack_counts=attack_counts,
        recent_logs=recent_logs
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
