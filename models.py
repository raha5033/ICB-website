from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<News {self.title}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    image_path = db.Column(db.String(200), default='default.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Event {self.title}>'

class AboutIslamPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text)
    image = db.Column(db.String(200), default='default.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 

    
class Classes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_title = db.Column(db.String(255), nullable=False)
    instructor_name = db.Column(db.String(255), nullable=False)
    target_group = db.Column(db.String(50), nullable=False)  # E.g., boys, girls, youth, adults
    age_group = db.Column(db.String(50), nullable=False)  # E.g., 4-8, 9-12, etc.
    course_fee = db.Column(db.String(50), nullable=False)  # E.g., Free, $50, etc.
    course_date = db.Column(db.DateTime, nullable=False)  # Course starting date
    frequency = db.Column(db.String(50), nullable=False)  # E.g., Every Sunday, Monthly
    location = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=True, default="default.jpg")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    content= db.Column(db.Text, nullable=True)

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    fee = db.Column(db.String(50), nullable=False)  # e.g., Free, $50
    details = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255), nullable=True)  # Donation link (if applicable)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Donation {self.title}>"




    def __repr__(self):
        return f"<Classes {self.course_title}>"
