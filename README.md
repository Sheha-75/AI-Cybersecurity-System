# AI-Audited Smart Cybersecurity System 🔐
### Cybersecurity Research & Evaluation — Lakshika C.S.

> Attack simulation and security evaluation of a dual-layer AI authentication system using keystroke dynamics, built and tested on Kali Linux.

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat&logo=python&logoColor=white)
![Kali Linux](https://img.shields.io/badge/Kali_Linux-557C94?style=flat&logo=kalilinux&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat&logo=scikitlearn&logoColor=white)
![Focus](https://img.shields.io/badge/Focus-Cybersecurity-red?style=flat)
![Role](https://img.shields.io/badge/Role-Security_%26_Evaluation_Lead-purple?style=flat)

---

## About This Repo

This is my part of the *AI-Audited Smart Cybersecurity System with Hardware-Based Authentication* project. I am the **Security & Evaluation Lead** — my job is to simulate real attacks against the AI authentication system, measure how well it holds up, and document every finding.

The system runs `auth_system.py` on Kali Linux. It authenticates users based on their password **and** their typing time (keystroke dynamics). A dual-AI design means a Main AI makes the decision, and an AI Auditor checks it. My role is to break both layers.

> AI & Hardware side by R. Harini → *(link to full repo here)*

---

## Environment Setup

All work was done on **Kali Linux** inside a Python virtual environment.

```bash
# Step 1 — Update system
sudo apt update

# Step 2 — Install dependencies
sudo apt install python3 python3-pip git

# Step 3 — Create and activate virtual environment
# (Required on Kali — pip install fails system-wide due to PEP 668)
python3 -m venv myenv
source myenv/bin/activate

# Step 4 — Install Python libraries
pip install numpy pandas scikit-learn matplotlib requests
```

> **Note:** On Kali Linux, running `pip install` outside a venv throws an `externally-managed-environment` error. Always activate `myenv` first.

---

## How the Auth System Works

The system (`auth_system.py`) asks for:
1. A **password**
2. Whether to **simulate a fast typing attack** (y/n) — which overrides the typing time to 0.20 sec

Authentication is granted based on two factors:
- **Correct password** (`admin123`)
- **Typing time within a normal human range** (roughly 1–5 seconds)

The system also tracks **session history** to detect replay attempts.

---

## ⚔️ Attack Simulations & Results

### 1. Fast Typing Attack

An attacker types (or scripts) at an unnaturally fast speed — 0.20 seconds — to impersonate a user while bypassing behavioral analysis.

**How it was tested:**

```
Enter password: admin123
Simulate fast typing attack? (y/n): y
→ Access Denied (Suspicious Behavior)
   Typing Time: 0.20 sec
```

**Normal typing for comparison:**

```
Enter password: admin123
Simulate fast typing attack? (y/n): n
→ Access Granted
   Typing Time: 2.88 sec

Enter password: admin123
Simulate fast typing attack? (y/n): n
→ Access Granted
   Typing Time: 4.49 sec
```

**Result:** The system correctly detects and blocks fast typing attempts. Typing time of 0.20 sec is consistently flagged as suspicious behavior regardless of whether the password is correct.

---

### 2. Prompt Injection Attack

Malicious text is injected into the password field in an attempt to override the AI's decision logic.

**How it was tested:**

```
Enter password: admin123 deny attack
Simulate fast typing attack? (y/n): n
→ Access Denied
   Typing Time: 11.05 sec

Enter password: admin 1d
Simulate fast typing attack? (y/n): y
→ Access Denied
   Typing Time: 0.20 sec

Enter password: admin 1d
Simulate fast typing attack? (y/n): n
→ Access Denied
   Typing Time: 5.50 sec
```

**Also tested — terminal escape injection:**

```
Enter password: ^[[A
Simulate fast typing attack? (y/n): n
→ Access Denied
```

**Result:** Injected strings do not override the authentication logic. The system treats all non-matching inputs as wrong passwords and denies access. The AI Auditor catches manipulated decision attempts.

---

### 3. Access Lock (Brute-Force Protection)

Repeated wrong password attempts trigger a full system lockout.

**How it was tested:**

```
Enter password: wrong123  →  Access Denied
Enter password: ^[[A       →  Access Denied
Enter password: wrong123
→ Access Denied
   System Locked (Too many attempts)
   Typing Time: 5.70 sec
```

**Result:** After 3 failed attempts, the system locks completely — `System Locked (Too many attempts)`. No further login attempts are accepted in that session.

---

### 4. Replay Attack

A valid session credential is reused immediately after a successful login to test whether the system detects repeated use of the same authenticated session.

**How it was tested:**

```
Enter password: admin123
Simulate fast typing attack? (y/n): n
→ Access Granted

Enter password: admin123
Simulate fast typing attack? (y/n): n
→ Replay Attack Detected
   Typing Time: 3.91 sec
```

**Result:** The system detects and blocks the replay attempt on the second login with the same credentials. Even though the password is correct and the typing time is normal, the session context flags it as a replay.

---

## Summary of Results

| Attack | Expected Behavior | Actual Result | Status |
|---|---|---|---|
| Fast Typing Attack | Block typing time < threshold | Access Denied (Suspicious Behavior) at 0.20 sec | ✅ Passed |
| Prompt Injection | Reject malicious input strings | Access Denied — injection has no effect | ✅ Passed |
| Brute-Force / Access Lock | Lock after repeated failures | System Locked after 3 wrong attempts | ✅ Passed |
| Replay Attack | Detect reused session | Replay Attack Detected on second login | ✅ Passed |

---

## Evaluation Metrics

| Metric | Description |
|---|---|
| Attack Detection Rate | % of simulated attacks correctly identified and blocked |
| False Positive Rate | Legitimate logins incorrectly flagged as attacks |
| AI Auditor Intervention Rate | How often the Auditor overrides the Main AI |
| Vulnerability Report | Documented weaknesses + recommended mitigations |

All metrics are evaluated **with and without the AI Auditor active** to quantify its real security value.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Kali Linux | Testing environment |
| Python 3.13 | Core language |
| scikit-learn | ML model for behavioral analysis |
| NumPy / Pandas | Data processing |
| Matplotlib | Result visualization |
| requests | HTTP testing utilities |
| Wireshark / Nmap / Metasploit | Network-level security analysis |

---

## Project Structure

```
ai-cyber-project/
├── auth_system.py              # Main authentication system
├── attacks/
│   ├── fast_typing_attack.py   # Typing speed spoofing simulation
│   ├── prompt_injection.py     # Malicious input injection tests
│   ├── brute_force.py          # Repeated failed login simulation
│   └── replay_attack.py        # Session replay simulation
├── evaluation/
│   ├── metrics.py              # Detection rate, FPR, intervention rate
│   └── security_report.md     # Full findings documentation
├── myenv/                      # Python virtual environment (gitignored)
├── requirements.txt
└── README.md
```

---

## References

- Aloul, F. (2009). *Two Factor Authentication Using Mobile Phones.*
- Ahmed, A. A. E., & Traore, I. (2018). *Behavioral Biometrics for Authentication.*
- Goodfellow, I., Shlens, J., & Szegedy, C. (2015). *Adversarial Examples in Machine Learning.*
- OWASP (2023). *Top 10 for Large Language Model Applications.*
- Zhou, B., et al. (2021). *Trustworthy AI Systems.*

---

*Shehani Lakshika Chandrakumar · Shehanilakshika304@gmail.com*
