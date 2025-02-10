from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import requests
from datetime import datetime, timedelta
import logging
from models import db, News, User, Event, AboutIslamPage
import os
from werkzeug.utils import secure_filename
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from models import AboutIslamPage
import sqlite3

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

DATABASE = os.path.join(app.instance_path, 'icb.db')

app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///icb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'assets', 'img')
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db.init_app(app)

def get_prayer_times():
    base_url = "http://localhost:8000/api/v1"
    mosque_id = "islamic-center-of-boulder-boulder-co-80303-united-states"
    
    try:
        # Get mosque data
        response_mosque = requests.get(f"{base_url}/{mosque_id}")
        
        if response_mosque.status_code != 200:
            raise requests.exceptions.RequestException("Failed to fetch data from API")
            
        mosque_data = response_mosque.json()
        
        # Get prayer times from times array
        prayer_times_array = mosque_data['rawdata']['times']
        # Get sunrise time
        sunrise_time = mosque_data['rawdata']['shuruq']
        # Get Juma time
        juma_time = mosque_data['rawdata']['jumua']
        
        # Get current month and day for iqama times
        current_date = datetime.now()
        month_index = current_date.month - 1  # Arrays are 0-based
        day = str(current_date.day)
        
        # Get iqama times from iqamaCalendar
        iqama_times = mosque_data['rawdata']['iqamaCalendar'][month_index][day]
        
        prayer_times = {}
        prayer_names = ['fajr', 'dhuhr', 'asr', 'maghrib', 'isha']
        
        # Add sunrise and juma times
        prayer_times['sunrise'] = datetime.strptime(sunrise_time, '%H:%M').strftime('%I:%M %p')
        prayer_times['juma'] = datetime.strptime(juma_time, '%H:%M').strftime('%I:%M %p')
        
        # Process each prayer time
        for i, prayer in enumerate(prayer_names):
            # Convert adhan time from times array
            adhan_time = datetime.strptime(prayer_times_array[i], '%H:%M')
            
            # Convert iqama time or calculate it if it's a delay
            if iqama_times[i].startswith('+'):
                # If it's a delay (e.g., "+10"), add minutes to adhan time
                delay_minutes = int(iqama_times[i].replace('+', ''))
                iqama_time = adhan_time + timedelta(minutes=delay_minutes)
            else:
                # If it's a fixed time (e.g., "13:30")
                iqama_time = datetime.strptime(iqama_times[i], '%H:%M')
            
            prayer_times[prayer] = {
                'adhan': adhan_time.strftime('%I:%M %p'),
                'iqama': iqama_time.strftime('%I:%M %p')
            }
        
        return prayer_times
        
    except Exception as e:
        print(f"Error fetching prayer times: {e}")
        # Fallback times
        return {
            'sunrise': '7:04 AM',
            'juma': '12:10 PM',  # Added juma to fallback times
            'fajr': {'adhan': '6:23 AM', 'iqama': '6:40 AM'},
            'dhuhr': {'adhan': '12:13 PM', 'iqama': '12:30 PM'},
            'asr': {'adhan': '1:55 PM', 'iqama': '2:15 PM'},
            'maghrib': {'adhan': '4:16 PM', 'iqama': '4:23 PM'},
            'isha': {'adhan': '5:53 PM', 'iqama': '7:30 PM'}
        }

# Define login_required decorator before routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function
@app.route('/code_of_conduct')
def code_of_conduct():
    return render_template('code_of_conduct.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/')

def index():
    news_items = News.query.order_by(News.created_at.desc()).limit(3).all()


    # Get all upcoming events (where date is >= current date)
    current_date = datetime.now()
    upcoming_events = Event.query.filter(Event.date >= current_date).order_by(Event.date).all()
    prayer_times = get_prayer_times()
    current_date_str = current_date.strftime('%B %d, %Y')
    return render_template('index.html', 
                         prayer_times=prayer_times,
                         current_date=current_date_str,
                         news_items=news_items,
                         events=upcoming_events)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin_news'))
        flash('Invalid username or password', 'error')
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/news')
@login_required
def admin_news():
    news_items = News.query.order_by(News.created_at.desc()).all()
    return render_template('admin/news.html', news_items=news_items)

@app.route('/admin/news/create', methods=['GET', 'POST'])
@login_required
def create_news():
    if request.method == 'POST':
        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = filename
        else:
            image_path = 'default.jpg'

        news = News(
            title=request.form['title'],
            content=request.form['content'],
            category=request.form['category'],
            event_date=datetime.strptime(request.form['event_date'], '%Y-%m-%d'),
            image_path=image_path
        )
        db.session.add(news)
        db.session.commit()
        flash('News created successfully!', 'success')
        return redirect(url_for('admin_news'))
    return render_template('admin/create_news.html')

@app.route('/admin/news/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    news = News.query.get_or_404(id)
    if request.method == 'POST':
        news.title = request.form['title']
        news.content = request.form['content']
        news.category = request.form['category']
        news.event_date = datetime.strptime(request.form['event_date'], '%Y-%m-%d')
        
        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            news.image_path = filename

        db.session.commit()
        flash('News updated successfully!', 'success')
        return redirect(url_for('admin_news'))
    return render_template('admin/edit_news.html', news=news)

@app.route('/admin/news/<int:id>/delete')
@login_required
def delete_news(id):
    news = News.query.get_or_404(id)
    db.session.delete(news)
    db.session.commit()
    flash('News deleted successfully!', 'success')
    return redirect(url_for('admin_news'))

@app.route('/admin/events')
@login_required
def admin_events():
    events = Event.query.order_by(Event.date).all()
    return render_template('admin/events.html', events=events)

@app.route('/admin/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'POST':
        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = filename
        else:
            image_path = 'default.jpg'

        event = Event(
            title=request.form['title'],
            content=request.form['content'],
            date=datetime.strptime(request.form['date'], '%Y-%m-%dT%H:%M'),
            location=request.form['location'],
            image_path=image_path
        )
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully!', 'success')
        return redirect(url_for('admin_events'))
    return render_template('admin/create_event.html')

@app.route('/admin/events/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    event = Event.query.get_or_404(id)
    if request.method == 'POST':
        event.title = request.form['title']
        event.content = request.form['content']
        event.date = datetime.strptime(request.form['date'], '%Y-%m-%dT%H:%M')
        event.location = request.form['location']
        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            event.image_path = filename
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('admin_events'))
    return render_template('admin/edit_event.html', event=event)

@app.route('/admin/events/<int:id>/delete')
@login_required
def delete_event(id):
    event = Event.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('admin_events'))

@app.context_processor
def inject_prayer_times():
    return {
        'prayer_times': get_prayer_times()
    }


@app.route('/about-islam/<slug>')
def about_islam_page(slug):
    # Get the page or return 404
    page = AboutIslamPage.query.filter_by(slug=slug).first_or_404()
    
    return render_template('about_islam.html', 
                         page=page)  # Pass the entire page object

@app.route('/admin/about-islam')
@login_required
def admin_about_islam():
    pages = AboutIslamPage.query.all()
    return render_template('admin/about_islam/list.html', pages=pages)

@app.route('/admin/about-islam/create', methods=['GET', 'POST'])
@login_required
def admin_about_islam_create():
    if request.method == 'POST':
        page = AboutIslamPage(
            title=request.form['title'],
            slug=request.form['slug'],
            content=request.form['content']
        )
        db.session.add(page)
        db.session.commit()
        flash('Page created successfully!', 'success')
        return redirect(url_for('admin_about_islam'))
    return render_template('admin/about_islam/create.html')

@app.route('/admin/about-islam/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_about_islam_edit(id):
    page = AboutIslamPage.query.get_or_404(id)
    if request.method == 'POST':
        page.title = request.form['title']
        page.slug = request.form['slug']
        page.content = request.form['content']
        db.session.commit()
        flash('Page updated successfully!', 'success')
        return redirect(url_for('admin_about_islam'))
    return render_template('admin/about_islam/edit.html', page=page)
@app.context_processor
def inject_about_islam_pages():
    """Make about_islam_pages available to all templates"""
    pages = AboutIslamPage.query.order_by(AboutIslamPage.title).all()
    return dict(about_islam_pages=pages)
@app.route('/admin/about-islam/<int:id>/delete')
@login_required
def admin_about_islam_delete(id):
    page = AboutIslamPage.query.get_or_404(id)
    db.session.delete(page)
    db.session.commit()
    flash('Page deleted successfully!', 'success')
    return redirect(url_for('admin_about_islam'))




# Helper function to get the database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE, timeout=10)  # Wait up to 10 seconds for the lock
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database and create tables (if they don't exist)
def init_db():
    # Ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Create Ramadhan Signups Table (if it doesn't exist)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ramadhan_signups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            email TEXT NOT NULL,
            date TEXT NOT NULL,
            details TEXT,
            UNIQUE(email, date)
        )
    ''')

    # Create Potluck Signups Table (if it doesn't exist)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS potluck_signups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            email TEXT NOT NULL,
            item TEXT NOT NULL,
            details TEXT
        )
    ''')

    conn.commit()
    conn.close()

# Call the function to initialize the database
init_db()

# Homepage
@app.route('/events')
def events():
    return render_template('events.html')

# Ramadhan Signup
@app.route('/ramadhan', methods=['GET', 'POST'])
def ramadhan():
    if request.method == 'POST':
        user_name = request.form['user_name']
        email = request.form['email']
        date = request.form['date']
        details = request.form.get('details', '')
        if date < "2025-03-01" or date > "2025-03-30":
            flash("You can only sign up between March 1 and March 30, 2025.", "error")
            return redirect(url_for('ramadhan'))
        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO ramadhan_signups (user_name, email, date, details) VALUES (?, ?, ?, ?)',
                (user_name, email, date, details)
            )
            conn.commit()
            flash('Thank you for signing up!', 'success')
        except sqlite3.IntegrityError:
            flash('You have already signed up for this date.', 'error')
        except sqlite3.OperationalError as e:
            flash(f'An error occurred: {str(e)}', 'error')
        finally:
            conn.close()

        return redirect(url_for('ramadhan'))

    # Fetch all signups to display on the calendar
    conn = get_db_connection()
    signups = conn.execute('SELECT * FROM ramadhan_signups').fetchall()
    conn.close()

    # Convert SQLite Row objects to a list of dictionaries
    signups_list = []
    for row in signups:
        signups_list.append({
            'user_name': row['user_name'],
            'email': row['email'],
            'date': row['date'],
            'details': row['details']
        })

    return render_template('ramadhan.html', signups=signups_list)

# Get signup details for a specific date
@app.route('/ramadhan/<date>')
def get_signup_details(date):
    conn = get_db_connection()
    signup = conn.execute('SELECT * FROM ramadhan_signups WHERE date = ?', (date,)).fetchone()
    conn.close()

    if signup:
        return {
            'user_name': signup['user_name'],
            'email': signup['email'],
            'details': signup['details']
        }
    else:
        return {'error': 'No signup found for this date.'}


# Potluck Signup
@app.route('/potluck', methods=['GET', 'POST'])
def potluck():
    conn = get_db_connection()  # Always initialize the database connection

    if request.method == 'POST':
        user_name = request.form['user_name']
        email = request.form['email']
        item = request.form['item']
        details = request.form.get('details', '')

        # Check if user has already signed up
        existing_signup = conn.execute(
            'SELECT * FROM potluck_signups WHERE email = ? AND item = ?', (email, item)
        ).fetchone()

        if existing_signup:
            flash("You have already signed up with this item!", "danger")
            conn.close()
            return redirect(url_for('potluck'))

        try:
            conn.execute(
                'INSERT INTO potluck_signups (user_name, email, item, details) VALUES (?, ?, ?, ?)',
                (user_name, email, item, details)
            )
            conn.commit()
            flash('Thank you for signing up!', 'success')
        except sqlite3.OperationalError as e:
            flash(f'An error occurred: {str(e)}', 'error')
        finally:
            conn.close()

        return redirect(url_for('potluck'))

    # Fetch all signups to display in the table
    signups = conn.execute('SELECT * FROM potluck_signups').fetchall()
    conn.close()

    return render_template('potluck.html', signups=signups)

@app.route('/api/potluck/signup', methods=['POST'])
def potluck_signup_api():
    data = request.json  # Receive JSON data from the frontend
    conn = get_db_connection()

    # Check if user already signed up
    existing_signup = conn.execute(
        'SELECT * FROM potluck_signups WHERE email = ? AND item = ?', (data['email'], data['item'])
    ).fetchone()

    if existing_signup:
        conn.close()
        return  flash(f'An error occurred: {str(e)}', 'error')


    # Insert the new signup
    try:
        conn.execute(
            'INSERT INTO potluck_signups (user_name, email, item, details) VALUES (?, ?, ?, ?)',
            (data['user_name'], data['email'], data['item'], data.get('details', ''))
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Signup successful!"}), 200
    except sqlite3.Error as e:
        conn.close()
        return jsonify({"error": f"Database error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)