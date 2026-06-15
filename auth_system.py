MAX_ATTEMPTS = 3
attempts = 0
previous_attempts = set()

import csv
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
import time

#Traning data: [typing_time, error_count]
x = [
    [2.5, 1],
    [3.0, 0],
    [2.0, 1],
    [0.5, 5],
    [0.3, 6],
    [6.0, 0]
]

#Labels: 1 = user,0 = attacker
y = [1, 1, 1, 0, 0, 0]

#Train model
model = RandomForestClassifier()
model.fit(x,y)

# Step 1: Capture typing behavior
def capture_input():
    print("Enter password:")
    start = time.time()
    password = input()
    end = time.time()

    typing_time = end - start

    print("Simulate fast typing attack? (y/n)")
    choice = input()

    if choice == "y":
        typing_time = 0.2

    return password, typing_time

# Step 2: Main AI (simple logic for now)
def main_ai(password, typing_time):
    correct_password = "admin123"

    # Detect prompt injection
    suspicious_words = ["ignore", "bypass", "override", "grant access"]

    for word in suspicious_words:
        if word in password.lower():
            return "DENY_INJECTION"

    # Error calculation
    error_count = sum(1 for a, b in zip(password, correct_password) if a != b)
    error_count += abs(len(password) - len(correct_password))

    prediction = model.predict([[typing_time, error_count]])

    if password != correct_password:
        return "DENY"

    if prediction[0] == 1:
        return "ALLOW"
    else:
        return "DENY"

# Step 3: AI Auditor
def ai_auditor(decision, typing_time):
    if decision == "ALLOW" and typing_time < 1:
        return "FLAGGED"
    return "OK"

# replyay
def detect_replay(password):
    if password in previous_attempts:
        return True

    previous_attempts.add(password)
    return False

def log_event(password, typing_time, decision, attack_type):
    with open("security_logs.csv", "a", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            datetime.now(),
            password,
            round(typing_time, 2),
            decision,
            attack_type
        ])
# Step 4: Run system
def run_system():
    global attempts

    while  True:

        password, typing_time = capture_input()

        if detect_replay(password):
            print(" Replay Attack Detected")
            log_event(password, typing_time, "DENY", "REPLAY")
            break

        decision = main_ai(password, typing_time)
        audit = ai_auditor(decision, typing_time)

        if decision == "DENY_INJECTION":
            print("Access Denied (Prompt Injection Detected)")
            attempts += 1
            log_event(password, typing_time, "DENY", "INJECTION")

        elif audit == "FLAGGED":
            print("Access Denied (Suspicious Behavior)")
            attempts += 1
            log_event(password, typing_time, "DENY", "SUSPICIOUS")

        elif decision == "ALLOW":
            print("Access Granted")
            attempts = 0
            log_event(password, typing_time, "ALLOW", "NORMAL")

        else:
            print("Access Denied")
            attempts += 1
            log_event(password, typing_time, "DENY", "WRONG_PASSWORD")

    # Lock system after too many attempts
        if attempts >= 3:
            print("System Locked (Too many attempts)")
            log_event(password, typing_time, "DENY", "LOCKED")
            break

    print(f"Typing Time: {typing_time:.2f} sec")

run_system()
