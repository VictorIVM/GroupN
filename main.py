from datetime import datetime, timedelta

from flask import Flask, render_template, url_for, request, session, redirect, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os
import random
import string


app = Flask(__name__)

# Setting up MySQL database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'mysqlpassword'
app.config['MYSQL_DB'] = 'voting_db'

mysql = mysql.connector.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    database=app.config['MYSQL_DB']
)
cursor = mysql.cursor(dictionary=True)

# Define the User model
class User:
    def __init__(self, id, first_name, last_name, email, password, role, course, admin_role, student_id):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.role = role
        self.course = course
        self.admin_role = admin_role
        self.student_id = student_id

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if 'user' in session:  # If user is already signed in, redirect to dashboard
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Query the User model to find a user with the provided email
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password) and user['role'] == 'admin':
            # Check if the user exists and the password is correct
            session['user'] = email  # Store user's email in session
            flash('You have been logged in!', 'success')
            return redirect(url_for('dashboard'))  # Redirect to dashboard after successful sign-in
        else:
            flash('Invalid username or password', 'error')

    return render_template('sign-in.html')


@app.route('/signin_student', methods=['GET', 'POST'])
def signin_student():
    if 'user' in session:  # If user is already signed in, redirect to dashboard
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Query the User model to find a user with the provided email
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password) and user['role'] == 'student':
            # Check if the user exists and the password is correct
            session['user'] = email  # Store user's email in session
            flash('You have been logged in!', 'success')
            return redirect(url_for('dashboard'))  # Redirect to dashboard after successful sign-in
        else:
            flash('Invalid username or password', 'error')

    return render_template('signin_student.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        registration_number = request.form['registration_number']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)  # Hash the password
        role = request.form['role']
        course = request.form.get('course', None)
        admin_role = request.form.get('admin_role', None)

        # Handle file upload
        picture = request.files['picture']
        if picture.filename != '':
            # Generate a random filename
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            _, file_extension = os.path.splitext(picture.filename)
            filename = f"{random_string}_{timestamp}{file_extension}"

            # Save the file to the uploads folder
            picture_path = os.path.join(app.root_path, 'static', 'uploads', filename)
            picture.save(picture_path)
            # Now, save the file path or name to the database along with other user information
        else:
            picture_path = None

        # Create a new user object with the hashed password
        insert_user_query = "INSERT INTO users (first_name, last_name, email, password, role, course, admin_role, student_id, picture) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_user_query, (
            first_name, last_name, email, hashed_password, role, course, admin_role, registration_number, filename))
        mysql.commit()
        flash('Your account has been created! You are now able to log in.', 'success')

        return redirect(url_for('signin'))

    return render_template('sign-up.html')


@app.route('/delete_user', methods=['POST'])
def delete_user():
    if request.method == 'POST':
        student_id = request.form['student_id']

        # Perform deletion of user with the specified student_id
        delete_query = "DELETE FROM users WHERE student_id = %s"
        cursor.execute(delete_query, (student_id,))
        mysql.commit()

        flash('User deleted successfully!', 'success')

    return redirect(url_for('voters'))


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if ('user' in session):
        return render_template('dashboard.html')
    return redirect(url_for('signin'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    return render_template('index.html')


@app.route("/ballot", methods=['GET', 'POST'])
def ballot():
    return render_template('ballot.html')


@app.route('/votes', methods=['GET', 'POST'])
def votes():
    cursor.execute(
        "SELECT positions.id, positions.description, position_time.starting_time, position_time.ending_time FROM positions LEFT JOIN position_time ON positions.id = position_time.position_id")
    positions = cursor.fetchall()

    # Calculate remaining time and determine status for each position
    for position in positions:
        if position['ending_time']:
            current_time = datetime.now()
            remaining_time = position['ending_time'] - current_time
            if remaining_time.total_seconds() > 0:
                days = remaining_time.days
                hours, remainder = divmod(remaining_time.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                position['remaining_time'] = f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
            else:
                position['remaining_time'] = "Expired"
            if current_time < position['starting_time']:
                position['status'] = 'Not Started'
            elif current_time > position['ending_time']:
                position['status'] = 'Ended'
            else:
                position['status'] = 'Running'
        else:
            position['remaining_time'] = None
            position['status'] = 'Not Set'

    return render_template('votes.html', positions=positions)


@app.route('/delete_position_time', methods=['POST'])
def delete_position_time():
    if request.method == 'POST':
        position_id = request.form['position_id']

        # Delete the position time from the database
        delete_query = "DELETE FROM position_time WHERE position_id = %s"
        cursor.execute(delete_query, (position_id,))
        mysql.commit()

        flash('Position time deleted successfully!', 'success')

    return redirect(url_for('votes'))


@app.route('/set_position_time', methods=['POST'])
def set_position_time():
    if request.method == 'POST':
        position_id = request.form['position_id']
        starting_time = request.form['starting_time']
        ending_time = request.form['ending_time']

        # Insert the position time into the database
        insert_query = "INSERT INTO position_time (position_id, starting_time, ending_time) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (position_id, starting_time, ending_time))
        mysql.commit()

        flash('Position time set successfully!', 'success')

    return redirect(url_for('votes'))


@app.route('/voters', methods=['GET', 'POST'])
def voters():
    cursor.execute("SELECT student_id, first_name, last_name, course, email, picture FROM users WHERE role = 'student'")
    student_users = cursor.fetchall()
    return render_template('voters.html', student_users=student_users)


@app.route('/nominate', methods=['GET', 'POST'])
def nominate():
    return render_template('nominate.html')


@app.route('/candidates', methods=['GET', 'POST'])
def candidates():
    cursor.execute("SELECT * FROM positions")
    positions = cursor.fetchall()
    # Fetch candidates from the database
    cursor.execute("SELECT * FROM candidates")
    candidates = cursor.fetchall()
    return render_template('candidates.html', positions=positions, candidates=candidates)





@app.route('/delete_candidate', methods=['POST'])
def delete_candidate():
    if request.method == 'POST':
        candidate_id = request.form['candidate_id']

        # Delete the candidate from the database
        delete_query = "DELETE FROM candidates WHERE id = %s"
        cursor.execute(delete_query, (candidate_id,))
        mysql.commit()

        flash('Candidate deleted successfully!', 'success')

    return redirect(url_for('candidates'))




# Define the upload folder path
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_candidate', methods=['POST'])
def add_candidate():
    if request.method == 'POST':
        position = request.form['position']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        student_id = request.form['student_id']

        if 'profile' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        profile = request.files['profile']

        if profile.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        if profile and allowed_file(profile.filename):
            # Generate a random filename
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            _, file_extension = os.path.splitext(profile.filename)
            filename = f"{random_string}_{timestamp}{file_extension}"

            # Ensure the upload directory exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

            # Save the file to the upload folder
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile.save(file_path)

            # Insert the new candidate into the database
            insert_query = "INSERT INTO candidates (position, profile, first_name, last_name, student_id) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (position, filename, first_name, last_name, student_id))
            mysql.commit()

            flash('Candidate added successfully!', 'success')
            return redirect(url_for('candidates'))

        else:
            flash('Allowed file types are png, jpg, jpeg, gif', 'error')
            return redirect(request.url)


@app.route('/get_user_details', methods=['POST'])
def get_user_details():
    if request.method == 'POST':
        student_id = request.form['student_id']
        query = "SELECT first_name, last_name FROM users WHERE student_id = %s AND role = 'student'"
        cursor.execute(query, (student_id,))
        user = cursor.fetchone()
        if user:
            return jsonify(user)
        else:
            return jsonify({'error': 'User not found'}), 404


@app.route('/positions', methods=['GET', 'POST'])
def positions():
    if request.method == 'GET':
        # Fetch positions from the database
        cursor.execute("SELECT * FROM positions")
        positions = cursor.fetchall()
        return render_template('positions.html', positions=positions)
    return redirect(url_for('signin'))


@app.route('/add_position', methods=['POST'])
def add_position():
    if request.method == 'POST':
        description = request.form['description']

        # Insert the new position into the database
        insert_query = "INSERT INTO positions (description) VALUES (%s)"
        cursor.execute(insert_query, (description,))
        mysql.commit()

        flash('Position added successfully!', 'success')

    return redirect(url_for('positions'))


@app.route('/delete_position', methods=['POST'])
def delete_position():
    if request.method == 'POST':
        position_id = request.form['position_id']

        # Delete the position from the database
        delete_query = "DELETE FROM positions WHERE id = %s"
        cursor.execute(delete_query, (position_id,))
        mysql.commit()

        flash('Position deleted successfully!', 'success')

    return redirect(url_for('positions'))



if __name__ == '__main__':
    app.secret_key = 'secret'  # Set your secret key
    app.run(debug=True)
