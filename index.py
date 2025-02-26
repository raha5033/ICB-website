from email.mime.text import MIMEText
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import requests
from datetime import datetime, timedelta
import logging
from models import Classes, db, News, User, Event, AboutIslamPage
import os
from werkzeug.utils import secure_filename
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from models import AboutIslamPage,Donation
import sqlite3
import pytz

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
        
        # Get mosque's timezone (e.g., 'America/Denver' for Boulder, CO)
        mosque_timezone = pytz.timezone('America/Denver')
        
        # Get current datetime in mosque's timezone
        current_datetime = datetime.now(mosque_timezone)
        
        # Extract today's Maghrib time to check if we need to adjust the date
        prayer_times_array = mosque_data['rawdata']['times']
        maghrib_time_str = prayer_times_array[3]  # Assuming index 3 is Maghrib
        
        # Parse Maghrib time
        maghrib_time = datetime.strptime(maghrib_time_str, '%H:%M').time()
        
        # Create a datetime object for today's Maghrib in the mosque's timezone
        maghrib_datetime = mosque_timezone.localize(
            datetime.combine(current_datetime.date(), maghrib_time)
        )
        
        # Check if current time is after Maghrib
       # if current_datetime > maghrib_datetime:
            # Use next day's date
       #     adjusted_date = current_datetime + timedelta(days=1)
        #else:
            # Use current date
        adjusted_date = current_datetime
        
        # Extract month and day from the adjusted date
        month_index = adjusted_date.month   # 0-based index
        day = str(adjusted_date.day)
        
        # Get iqama times for the adjusted date
        iqama_times = mosque_data['rawdata']['iqamaCalendar'][month_index][day]
        
        # Process prayer times as before
        prayer_times = {}
        prayer_names = ['fajr', 'dhuhr', 'asr', 'maghrib', 'isha']
        
        # Add sunrise and juma times
        prayer_times['sunrise'] = datetime.strptime(mosque_data['rawdata']['shuruq'], '%H:%M').strftime('%I:%M %p')
        prayer_times['juma'] = datetime.strptime(mosque_data['rawdata']['jumua'], '%H:%M').strftime('%I:%M %p')
        
        for i, prayer in enumerate(prayer_names):
            adhan_time = datetime.strptime(prayer_times_array[i], '%H:%M')
            
            if iqama_times[i].startswith('+'):
                delay_minutes = int(iqama_times[i].replace('+', ''))
                iqama_time = adhan_time + timedelta(minutes=delay_minutes)
            else:
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
            'juma': '12:10 PM',
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
     # Attempt to fetch class_entry but don't fail if not found
    all_classes = Classes.query.order_by(Classes.course_date).all()
    pages = AboutIslamPage.query.all()
    news_items = News.query.order_by(News.created_at.desc()).all()
    Donations=Donation.query.all()
    return render_template(
        'code_of_conduct.html',
        classes=all_classes,
        about_islam_pages=pages,
        news_items=news_items,Donations=Donations
    )

@app.route('/')
@app.route('/index.html')
def index():
    Donations=Donation.query.all()
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
                         events=upcoming_events,
                         Donations=Donations)

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

@app.route('/news/<int:id>')
def view_news(id):
    news = News.query.get_or_404(id)  # Ensures news exists

    # Attempt to fetch class_entry but don't fail if not found
    class_entry = Classes.query.get(id)  # Use `.get()` instead of `.get_or_404()`

    all_classes = Classes.query.order_by(Classes.course_date).all()
    pages = AboutIslamPage.query.all()
    news_items = News.query.order_by(News.created_at.desc()).all()
    Donations=Donation.query.all()

    return render_template(
        'view_news.html',
        news=news,
        class_entry=class_entry,  # Could be None if not found
        classes=all_classes,
        about_islam_pages=pages,
        news_items=news_items,Donations=Donations
    )
@app.route('/news')
def view_all_news():

    # Attempt to fetch class_entry but don't fail if not found
   
    news = News.query.order_by(News.created_at).all()

    return render_template(
        'view_all_news.html',

        news_items=news
    )

@app.route('/classes')
def classes():
    all_classes = Classes.query.order_by(Classes.course_date).all()
    pages = AboutIslamPage.query.all()
    news_items = News.query.order_by(News.created_at.desc()).all()
    Donations=Donation.query.all()

    return render_template('classes.html', Donations=Donations,classes=all_classes,about_islam_pages=pages,news_items=news_items)
@app.context_processor
def inject_classes():
    """Make classes available to all templates"""
    classes = Classes.query.order_by(Classes.course_date).all()
    return dict(all_classes=classes)  # Rename to avoid conflict with route variable
@app.route('/classes/<int:id>')
def class_detail(id):
    class_entry = Classes.query.get_or_404(id)
    all_classes = Classes.query.order_by(Classes.course_date).all()
    pages = AboutIslamPage.query.all()
    news_items = News.query.order_by(News.created_at.desc()).all()
    Donations=Donation.query.all()
    return render_template('class.html',Donations=Donations, class_entry=class_entry,classes=all_classes,about_islam_pages=pages,news_items=news_items)

@app.route('/about-islam/<slug>')
def about_islam_page(slug):
    # Get the page or return 404
    page = AboutIslamPage.query.filter_by(slug=slug).first_or_404()
    pages = AboutIslamPage.query.all()
    news_items = News.query.order_by(News.created_at.desc()).all()
    return render_template('about_islam.html', 
                         page=page,pages=pages,
                        news_items=news_items )  # Pass the entire page object
@app.route('/about-islam')
def about_islam_pages():
    
    pages = AboutIslamPage.query.all()
    news_items = News.query.order_by(News.created_at.desc()).all()
    classes = Classes.query.order_by(Classes.course_date).all()
    Donations=Donation.query.all()

    return render_template('about_islam_pages.html',Donations=Donations, classes=classes, pages=pages,
                        news_items=news_items)

@app.route('/admin/about-islam')
@login_required
def admin_about_islam():
    pages = AboutIslamPage.query.all()
    return render_template('admin/about_islam/list.html', pages=pages)

@app.route('/admin/about-islam/create', methods=['GET', 'POST'])
@login_required
def admin_about_islam_create():
    if request.method == 'POST':
        title = request.form['title']  # ✅ Remove trailing commas
        slug = request.form['slug']
        content = request.form['content']

        image = request.files.get('image')  # ✅ Use .get() to avoid KeyError
        image_path = "default.jpg"  # ✅ Default image

        if image and image.filename:  # ✅ Ensure an image is uploaded
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = filename  # ✅ Store filename only

        # ✅ Use a different variable name instead of overwriting `AboutIslamPage`
        new_page = AboutIslamPage(
            title=title,
            slug=slug,
            image=image_path,
            content=content
        )

        db.session.add(new_page)  # ✅ Use new_page instead of overwriting class
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

        # Handle new image upload
        image = request.files['image']
        if image and image.filename:  # Ensure a file was uploaded
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)  # Save the new image
            page.image = filename  # Update the image field

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
    events = Event.query.order_by(Event.date).all()
    pages = AboutIslamPage.query.all()
    news_items = News.query.order_by(News.created_at.desc()).all()
    Donations=Donation.query.all()

    return render_template('events.html', Donations=Donations,events=events,about_islam_pages=pages,news_items=news_items)

@app.route('/event/<int:id>')
def event_details(id):
    events = Event.query.get_or_404(id)
    all_classes = Classes.query.order_by(Classes.course_date).all()
    pages = AboutIslamPage.query.all()
    news_items = News.query.order_by(News.created_at.desc()).all()
    Donations=Donation.query.all()
    return render_template('event.html',Donations=Donations, item=events,classes=all_classes,about_islam_pages=pages,news_items=news_items)

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
# @app.route('/potluck', methods=['GET', 'POST'])
# def potluck():
#     conn = get_db_connection()  # Always initialize the database connection

#     if request.method == 'POST':
#         user_name = request.form['user_name']
#         email = request.form['email']
#         item = request.form['item']
#         details = request.form.get('details', '')

#         # Check if user has already signed up
#         existing_signup = conn.execute(
#             'SELECT * FROM potluck_signups WHERE email = ? AND item = ?', (email, item)
#         ).fetchone()

#         if existing_signup:
#             flash("You have already signed up with this item!", "danger")
#             conn.close()
#             return redirect(url_for('potluck'))

#         try:
#             conn.execute(
#                 'INSERT INTO potluck_signups (user_name, email, item, details) VALUES (?, ?, ?, ?)',
#                 (user_name, email, item, details)
#             )
#             conn.commit()
#             flash('Thank you for signing up!', 'success')
#         except sqlite3.OperationalError as e:
#             flash(f'An error occurred: {str(e)}', 'error')
#         finally:
#             conn.close()

#         return redirect(url_for('potluck'))

#     # Fetch all signups to display in the table
#     signups = conn.execute('SELECT * FROM potluck_signups').fetchall()
#     conn.close()

#     return render_template('potluck.html', signups=signups)
@app.route('/potluck')
def potluck_masjid():
    # Attempt to fetch class_entry but don't fail if not found
    all_classes = Classes.query.order_by(Classes.course_date).all()
    pages = AboutIslamPage.query.all()
    news_items = News.query.order_by(News.created_at.desc()).all()
    Donations=Donation.query.all()

    return render_template(
        'potluck_masjid.html',
        classes=all_classes,
        about_islam_pages=pages,
        news_items=news_items,Donations=Donations
    )
    

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

#classes routes
@app.route('/admin/classes')
@login_required
def admin_classes():
    classes = Classes.query.order_by(Classes.course_date).all()
    return render_template('admin/classes/list.html', classes=classes)

@app.route('/admin/classes/create', methods=['GET', 'POST'])
@login_required
def create_class():
    if request.method == 'POST':
        course_title = request.form['course_title']
        instructor_name = request.form['instructor_name']
        target_group = request.form['target_group']
        age_group = request.form['age_group']
        course_fee = request.form['course_fee']
        course_date = datetime.strptime(request.form['course_date'], '%Y-%m-%dT%H:%M')
        frequency = request.form['frequency']
        location = request.form['location']
        content= request.form['content']

        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = filename
        else:
            image_path = "default.jpg"

        new_class = Classes(
            course_title=course_title,
            instructor_name=instructor_name,
            target_group=target_group,
            age_group=age_group,
            course_fee=course_fee,
            course_date=course_date,
            frequency=frequency,
            location=location,
            image=image_path,
            content=content
        )

        db.session.add(new_class)
        db.session.commit()
        flash("Class created successfully!", "success")
        return redirect(url_for('admin_classes'))

    return render_template('admin/classes/create.html')


@app.route('/admin/classes/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_class(id):
    class_entry = Classes.query.get_or_404(id)

    if class_entry.content is None:  # Ensure content is not None
        class_entry.content = ""

    if request.method == 'POST':
        class_entry.course_title = request.form['course_title']
        class_entry.instructor_name = request.form['instructor_name']
        class_entry.target_group = request.form['target_group']
        class_entry.age_group = request.form['age_group']
        class_entry.course_fee = request.form['course_fee']
        class_entry.course_date = datetime.strptime(request.form['course_date'], '%Y-%m-%dT%H:%M')
        class_entry.frequency = request.form['frequency']
        class_entry.location = request.form['location']
        class_entry.content = request.form['content'] if request.form['content'] else ""

        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            class_entry.image = filename

        db.session.commit()
        flash("Class updated successfully!", "success")
        return redirect(url_for('admin_classes'))

    return render_template('admin/classes/edit.html', class_entry=class_entry)

@app.route('/admin/classes/<int:id>/delete')
@login_required
def delete_class(id):
    class_entry = Classes.query.get_or_404(id)
    db.session.delete(class_entry)
    db.session.commit()
    flash("Class deleted successfully!", "success")
    return redirect(url_for('admin_classes'))



@app.route('/masjid-calendar')
def masjid_calendar():
    """Render the calendar page."""
    news_items = News.query.order_by(News.created_at.desc()).limit(6).all()
    pages = AboutIslamPage.query.all()
    return render_template('masjid_calendar.html',news_items=news_items,  # ✅ Now passing news_items
        about_islam_pages=pages)

@app.route('/api/events')
def get_events():
    """Fetch all events with a date from the database and return as JSON."""
    events = []

    # Fetch all data with dates
    
    classes = Classes.query.all()
    news_items = News.query.all()
    general_events = Event.query.all()

    # Convert each to the required JSON format
    

    for c in classes:
        events.append({
            "title": c.course_title,
            "start": c.course_date.strftime('%Y-%m-%d'),
            "url": url_for('class_detail', id=c.id),
            "color": "#007BFF"
        })

    for n in news_items:
        events.append({
            "title": n.title,
            "start": n.event_date.strftime('%Y-%m-%d'),
            "url": url_for('view_news', id=n.id),
            "color": "#28A745"
        })

    for e in general_events:
        events.append({
            "title": e.title,
            "start": e.date.strftime('%Y-%m-%d'),
            "url": url_for('event_details',id=e.id),
            "color": "#6C757D"
        })

    return jsonify(events)

#forms
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        subject = request.form['subject']
        message = request.form['message']
        inquiry_type = request.form['inquiry_type']

        # Mapping inquiry type to email recipients
        email_recipients = {
            "fundraising": "contact.icb@gmail.com",
            "reserving_space": "contact.icb@gmail.com",
            "scheduling_event": "contact.icb@gmail.com",
            "financial_assistance": "contact.icb@gmail.com",
            "zakat": "contact.icb@gmail.com",
            "nikah": "contact.icb@gmail.com",
            "islam": "contact.icb@gmail.com",
            "others": "contact.icb@gmail.com",
        }

        recipient_email = email_recipients.get(inquiry_type, "contact.icb@gmail.com")  # Default email

        # Construct Email Message
        msg = MIMEMultipart()
        msg['From'] = email  # Your email address
        msg['To'] = recipient_email
        msg['Subject'] = f"New Inquiry: {subject}"

        email_body = f"""
        Name: {name}
        Email: {email}
        Phone: {phone}

        Message:
        {message}
        """

        msg.attach(MIMEText(email_body, 'plain'))

        try:
            # SMTP Server Configuration (Modify based on your email provider)
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            smtp_username = "contact.icb@gmail.com"  # Your email address
            smtp_password = "l1is5$dRC6ZFOG#I"  # Your email password

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, recipient_email, msg.as_string())
            server.quit()

            flash('Your message has been sent successfully!', 'success')
        except Exception as e:
            flash(f'Error sending email: {e}', 'error')

        return redirect(url_for('contact'))

    return render_template('contact.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/donation')
def donation():
    Donations=Donation.query.all()
    return render_template('donation.html',Donations=Donations)
@app.route('/admin/donations/create', methods=['GET', 'POST'])
@login_required
def create_donation():
    if request.method == 'POST':
        title = request.form['title']
        fee = request.form['fee']
        details = request.form['details']
        link = request.form['link']

        new_donation = Donation(
            title=title,
            fee=fee,
            details=details,
            link=link
        )

        db.session.add(new_donation)
        db.session.commit()
        flash('Donation added successfully!', 'success')
        return redirect(url_for('admin_donations'))

    return render_template('admin/donations/create.html')

@app.route('/admin/donations')
@login_required
def admin_donations():
    donations = Donation.query.order_by(Donation.created_at.desc()).all()
    return render_template('admin/donations/list.html', donations=donations)
@app.route('/admin/donations/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_donation(id):
    donation = Donation.query.get_or_404(id)

    if request.method == 'POST':
        donation.title = request.form['title']
        donation.fee = request.form['fee']
        donation.details = request.form['details']
        donation.link = request.form['link']

        db.session.commit()
        flash('Donation updated successfully!', 'success')
        return redirect(url_for('admin_donations'))

    return render_template('admin/donations/edit.html', donation=donation)
@app.route('/admin/donations/<int:id>/delete')
@login_required
def delete_donation(id):
    donation = Donation.query.get_or_404(id)
    db.session.delete(donation)
    db.session.commit()
    flash('Donation deleted successfully!', 'success')
    return redirect(url_for('admin_donations'))

if __name__ == '__main__':
    app.run(debug=True)