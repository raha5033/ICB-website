import sqlite3
import bcrypt

# Hash the new password
new_password = 'icb'.encode('utf-8')
hashed_password = bcrypt.hashpw(new_password, bcrypt.gensalt())

# Update the database
conn = sqlite3.connect('icb.db')
cursor = conn.cursor()

# Parameterized query to prevent SQL injection
cursor.execute(
    "UPDATE users SET password = ? WHERE username = ?",
    (hashed_password, 'admin')
)

conn.commit()
conn.close()