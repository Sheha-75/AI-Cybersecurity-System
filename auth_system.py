import time
import csv
import sqlite3
from datetime import datetime

import bcrypt
import numpy as np
from sklearn.ensemble import RandomForestClassifier

MAX_ATTEMPTS = 3

attempts = 0
previous_attempts = set()
failed_attempts = {}

# -----------------------------
# Train AI model
# -----------------------------

X = np.array([
    [2.0, 0],
    [3.0, 0],
    [4.0, 0],
    [5.0, 0],
    [8.0, 0],

    [0.2, 5],
    [0.5, 4],
    [0.8, 3],

    [3.0, 5],
    [5.0, 4]
])

y = np.array([
    1, 1, 1, 1, 1,
    0, 0, 0,
    0, 0
])

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X, y)


# -----------------------------
# Database
# -----------------------------

def get_user_hash(username):
    conn = sqlite3.connect("security.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password_hash FROM users WHERE username = ?",
        (username,)
    )

    result = cursor.fetchone()

    conn.close()

    return result[0] if result else None


# -----------------------------
# Logging
# -----------------------------

def log_event(
    username,
    typing_time,
    decision,
    attack_type
):
    with open(
        "security_logs.csv",
        "a",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            datetime.now(),
            username,
            round(typing_time, 2),
            decision,
            attack_type
        ])


# -----------------------------
# Replay Detection
# -----------------------------

def detect_replay(
    username,
    password,
    typing_time
):
    attempt = (
        username,
        password,
        round(typing_time, 1)
    )

    if attempt in previous_attempts:
        return True

    previous_attempts.add(attempt)

    return False


# -----------------------------
# Risk Scoring
# -----------------------------

def calculate_risk(
    typing_time,
    failed_attempts_count,
    replay=False,
    injection=False
):
    score = 0

    if typing_time < 1:
        score += 40

    score += failed_attempts_count * 10

    if replay:
        score += 20

    if injection:
        score += 50

    return min(score, 100)


# -----------------------------
# AI Authentication
# -----------------------------

def main_ai(
    username,
    password,
    typing_time,
    replay=False
):
    correct_password = get_user_hash(username)

    if correct_password is None:
        return "DENY", 100

    if username not in failed_attempts:
        failed_attempts[username] = 0

    suspicious_words = [
        "ignore",
        "bypass",
        "override",
        "grant access"
    ]

    injection = any(
        word in password.lower()
        for word in suspicious_words
    )

    if not bcrypt.checkpw(
        password.encode(),
        correct_password
    ):
        failed_attempts[username] += 1
        return "DENY", 100

    error_count = 0

    prediction = model.predict(
        [[typing_time, error_count]]
    )

    risk_score = calculate_risk(
        typing_time=typing_time,
        failed_attempts_count=failed_attempts[username],
        replay=replay,
        injection=injection
    )

    print(
        f"DEBUG -> typing_time={typing_time:.2f}"
    )

    print(
        f"Risk Score: {risk_score}"
    )

    if prediction[0] == 1 and risk_score <= 30:
        failed_attempts[username] = 0
        return "ALLOW", risk_score

    failed_attempts[username] += 1

    return "DENY", risk_score


# -----------------------------
# Auditor Layer
# -----------------------------

def ai_auditor(
    decision,
    typing_time
):
    if decision == "ALLOW" and typing_time < 1:
        return "FLAGGED"

    return "OK"


# -----------------------------
# Terminal Input
# -----------------------------

def capture_input():
    username = input(
        "Enter username: "
    )

    print("Enter password:")

    start = time.time()
    password = input()
    end = time.time()

    typing_time = end - start

    choice = input(
        "Simulate fast typing attack? (y/n): "
    )

    if choice.lower() == "y":
        typing_time = 0.2

    return username, password, typing_time


# -----------------------------
# Terminal Mode
# -----------------------------

def run_system():
    global attempts

    while True:

        username, password, typing_time = capture_input()

        replay = detect_replay(
            username,
            password,
            typing_time
        )

        if replay:
            print("🚨 Replay Attack Detected")

            log_event(
                username,
                typing_time,
                "DENY",
                "REPLAY"
            )

            break

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

        if audit == "FLAGGED":

            print(
                "❌ Access Denied (Suspicious Behavior)"
            )

            attempts += 1

            log_event(
                username,
                typing_time,
                "DENY",
                "SUSPICIOUS"
            )

        elif decision == "ALLOW":

            print("✅ Access Granted")
            print(
                f"Risk Score: {risk_score}/100"
            )

            attempts = 0

            log_event(
                username,
                typing_time,
                "ALLOW",
                "NORMAL"
            )

            break

        else:

            print("❌ Access Denied")
            print(
                f"Risk Score: {risk_score}/100"
            )

            attempts += 1

            log_event(
                username,
                typing_time,
                "DENY",
                "FAILED_LOGIN"
            )

        if attempts >= MAX_ATTEMPTS:

            print(
                "🚨 System Locked (Too many attempts)"
            )

            log_event(
                username,
                typing_time,
                "DENY",
                "LOCKED"
            )

            break


if __name__ == "__main__":
    run_system()
