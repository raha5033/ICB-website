from flask import Flask
from werkzeug.security import generate_password_hash


password = "icbAdmin"
hashed_password = generate_password_hash(password, method="scrypt")

print(hashed_password)
