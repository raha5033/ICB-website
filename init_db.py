from index import app, db
from models import News, User, Event
from datetime import datetime
from werkzeug.security import generate_password_hash

with app.app_context():
    # Drop all tables first to ensure a clean slate
    db.drop_all()
    # Create all tables
    db.create_all()
    
    # Create sample news items
    sample_news = [
        News(
            title='Black History Month',
            content='Join us for a lecture on the history of Black History Month.',
            category='Lecture',
            event_date=datetime.strptime('2025-03-01', '%Y-%m-%d'),
            image_path='black history.png'
        ),
        News(
            title='Iftar and Taraweeh',
            content='Come and join us for Iftar and Taraweeh.',
            category='Taraweeh',
            event_date=datetime.strptime('2025-03-15', '%Y-%m-%d'),
            image_path='iftar.jpg'
        ),
        News(
            title='Visit Us for Open House',
            content='We invite all to visit us for our Open House.',
            category='Open House',
            event_date=datetime.strptime('2025-03-20', '%Y-%m-%d'),
            image_path='open house.jpg'
        )
    ]
    
    # Add sample news to database
    for news in sample_news:
        db.session.add(news)
    
    # Add admin user
    admin_user = User(
        username='admin',
        password=generate_password_hash('admin123'),
        is_admin=True
    )
    db.session.add(admin_user)
    
    # Add sample events
    sample_events = [
        Event(
            title='Friday Prayer',
            content='Join us for the weekly Friday prayer service. Sheikh Ahmed will deliver the khutbah.',
            date=datetime.strptime('2024-03-15 13:30', '%Y-%m-%d %H:%M'),
            location='Main Prayer Hall',
            image_path='prayer.jpg'
        ),
        Event(
            title='Islamic Classes',
            content='Weekly Islamic studies class covering Tafsir and Hadith. All are welcome.',
            date=datetime.strptime('2024-03-20 18:00', '%Y-%m-%d %H:%M'),
            location='Classroom 1',
            image_path='class.jpg'
        )
    ]
    
    for event in sample_events:
        db.session.add(event)
    
    # Commit all changes
    db.session.commit()
    
    print("Database tables created and sample data added successfully!") 