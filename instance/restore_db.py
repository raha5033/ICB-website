from index import app, db
from models import News, User, Event
from datetime import datetime
from werkzeug.security import generate_password_hash
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('icb.db')
cursor = conn.cursor()

# Drop all tables (optional: use with caution)
db.drop_all()

# Create tables again
db.create_all()

# Load existing data from the SQL dump file
with open('icb_backup.sql', 'r', encoding='utf-8') as f:
    sql_script = f.read()

# Execute the SQL script to restore data
cursor.executescript(sql_script)

# Commit changes and close connection
conn.commit()
conn.close()

print("Database restored successfully from backup!")
