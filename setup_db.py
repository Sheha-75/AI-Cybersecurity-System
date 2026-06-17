import sqlite3
import bcrypt

conn = sqlite3.connect("security.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password_hash BLOB NOT NULL
)
""")

users = [
    ("admin", bcrypt.hashpw(b"admin123", bcrypt.gensalt())),
    ("shehani", bcrypt.hashpw(b"cyber2026", bcrypt.gensalt())),
    ("guest", bcrypt.hashpw(b"guest123", bcrypt.gensalt()))
]

cursor.executemany(
    "INSERT OR REPLACE INTO users VALUES (?, ?)",
    users
)

conn.commit()
conn.close()

print("Database initialized.")
