import sqlite3

conn = sqlite3.connect("buspass.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bus_passes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    source TEXT NOT NULL,
    destination TEXT NOT NULL,
    pass_type TEXT NOT NULL,
    price REAL NOT NULL,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

conn.commit()
conn.close()

print("Database created successfully!")
