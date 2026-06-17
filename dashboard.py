import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("security_logs.csv")

print("\n=== Security Summary ===\n")

print(f"Total attempts: {len(df)}")

successful = len(df[df["decision"] == "ALLOW"])
failed = len(df[df["decision"] == "DENY"])

print(f"Successful logins: {successful}")
print(f"Denied logins: {failed}")

print("\nAttack counts:\n")
print(df["attack_type"].value_counts())

df["attack_type"].value_counts().plot(kind="bar")

plt.title("Attack Types")
plt.xlabel("Attack")
plt.ylabel("Count")

plt.tight_layout()
plt.show()
