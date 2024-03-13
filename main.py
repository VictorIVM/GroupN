from datetime import datetime, timedelta

from flask import Flask, render_template, url_for, request, session, redirect, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os
import random
import string
import cv2
import numpy as np  # Import numpy for array operations

app = Flask(__name__)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Setting up MySQL database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
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
    if 'user' in session:
        return redirect(url_for('dashboard_student'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        picture = request.files['picture']  # Get the uploaded file object

        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password) and user['role'] == 'student':
            # Perform face recognition
            img_data = np.fromstring(picture.read(), np.uint8)  # Read image data from the file object
            img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)  # Decode the image data
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)  # Detect faces

            if len(faces) == 1:  # Assuming only one face is detected
                # Face recognized, allow sign-in
                session['user'] = email
                return redirect(url_for('dashboard_student'))
            else:
                flash('Face recognition failed. Please try again.', 'error')
        else:
            flash('Invalid username or password', 'error')

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
    if 'user' in session:
        return redirect(url_for('dashboard_student'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        picture = request.files['picture']  # Get the uploaded file object

        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password) and user['role'] == 'student':
            # Perform face recognition
            img_data = np.fromstring(picture.read(), np.uint8)  # Read image data from the file object
            img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)  # Decode the image data
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)  # Detect faces

            if len(faces) == 1:  # Assuming only one face is detected
                # Face recognized, allow sign-in
                session['user'] = email
                return redirect(url_for('dashboard_student'))
            else:
                flash('Face recognition failed. Please try again.', 'error')
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

        return redirect(url_for('dashboard'))

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
    if 'user' in session:
        # Fetch positions from the database
        cursor.execute("SELECT positions.id, positions.description FROM positions")
        positions = cursor.fetchall()

        # For each position, fetch candidates and their votes
        for position in positions:
            cursor.execute("SELECT candidates.id, candidates.first_name, candidates.last_name, COUNT(ballot.id) AS votes \
                                FROM candidates LEFT JOIN ballot ON candidates.id = ballot.candidate_id \
                                WHERE candidates.position_id = %s \
                                GROUP BY candidates.id", (position['id'],))
            position['candidates'] = cursor.fetchall()

        return render_template('dashboard.html', positions=positions)
    return redirect(url_for('signin'))


@app.route('/dashboard_student', methods=['GET', 'POST'])
def dashboard_student():
    if 'user' in session:
        return render_template('dashboard_student.html')
    return redirect(url_for('signin_student'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    return render_template('index.html')


# Route to display the ballot
@app.route("/ballot", methods=['GET', 'POST'])
def ballot():
    if 'user' in session:
        email = session['user']
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user:
            user_id = user['id']
            if request.method == 'GET':
                # Fetch positions and candidates from the database
                cursor.execute(
                    "SELECT positions.*, position_time.starting_time, position_time.ending_time FROM positions LEFT JOIN position_time ON positions.id = position_time.position_id")
                positions = cursor.fetchall()

                candidates_by_position = {}
                voted_candidates = {}  # Store voted candidates' information

                current_time = datetime.now()

                for position in positions:
                    # Calculate status and remaining time for each position
                    if position['starting_time'] and position['ending_time']:
                        if position['starting_time'] <= current_time <= position['ending_time']:
                            position['status'] = 'Running'
                            position['remaining_time'] = (position['ending_time'] - current_time).total_seconds()
                        elif position['ending_time'] < current_time:
                            position['status'] = 'Ended'
                            position['remaining_time'] = 0
                        else:
                            position['status'] = 'Not Started'
                            position['remaining_time'] = None
                    else:
                        position['status'] = 'Not Set'
                        position['remaining_time'] = None

                    # Fetch candidates for the position
                    cursor.execute("SELECT * FROM candidates WHERE position_id = %s", (position['id'],))
                    candidates_by_position[position['id']] = cursor.fetchall()

                    # Fetch voted candidate's information for each position
                    cursor.execute(
                        "SELECT candidates.*, ballot.voter_id FROM candidates INNER JOIN ballot ON candidates.id = ballot.candidate_id WHERE ballot.position_id = %s AND ballot.voter_id = %s",
                        (position['id'], user_id))
                    voted_candidate = cursor.fetchone()
                    if voted_candidate:
                        voted_candidates[position['id']] = voted_candidate

                return render_template('ballot.html', positions=positions,
                                       candidates_by_position=candidates_by_position, voted_candidates=voted_candidates)
            elif request.method == 'POST':
                # Handle form submission for casting votes
                position_id = request.form['position_id']
                candidate_id = request.form['candidate_id']

                # Check if the user has already voted for this position
                check_query = "SELECT * FROM ballot WHERE position_id = %s AND voter_id = %s"
                cursor.execute(check_query, (position_id, user_id))
                existing_vote = cursor.fetchone()
                if existing_vote:
                    flash('You have already voted for this position', 'error')
                else:
                    # Insert the vote into the database
                    insert_query = "INSERT INTO ballot (position_id, candidate_id, voter_id) VALUES (%s, %s, %s)"
                    cursor.execute(insert_query, (position_id, candidate_id, user_id))
                    mysql.commit()
                    flash('Vote cast successfully', 'success')
                # Redirect to the same route to refresh the page and display the voted candidate
                return redirect(url_for('ballot'))
    else:
        return redirect(url_for('signin'))


# Route to get candidates for a particular position via AJAX


@app.route('/get_candidates', methods=['GET'])
def get_candidates():
    if request.method == 'GET':
        position_id = request.args.get('position_id')  # Get the position_id from the request arguments
        if position_id:
            cursor.execute("SELECT * FROM candidates WHERE position_id = %s", (position_id,))
            candidates = cursor.fetchall()
            return jsonify(candidates)  # Return the candidate data as JSON
        else:
            return jsonify({'error': 'Position ID not provided'})


# Route to handle the vote casting process via AJAX


@app.route('/cast_vote', methods=['POST'])
def cast_vote():
    if request.method == 'POST':
        position_id = request.form['position_id']
        candidate_id = request.form['candidate_id']
        voter_email = session.get('user')  # Retrieve user email from session

        # Retrieve user ID from the database using user email
        cursor.execute("SELECT id FROM users WHERE email = %s", (voter_email,))
        user = cursor.fetchone()
        if user:
            voter_id = user['id']

            # Check if the user has already voted for this position
            check_query = "SELECT * FROM ballot WHERE position_id = %s AND voter_id = %s"
            cursor.execute(check_query, (position_id, voter_id))
            existing_vote = cursor.fetchone()
            if existing_vote:
                return jsonify({'status': 'error', 'message': 'You have already voted for this position'})
            else:
                # Insert the vote into the database
                insert_query = "INSERT INTO ballot (position_id, candidate_id, voter_id) VALUES (%s, %s, %s)"
                cursor.execute(insert_query, (position_id, candidate_id, voter_id))
                mysql.commit()
                return jsonify({'status': 'success', 'message': 'Vote cast successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'User not found'})


# Modify the ballot.html to display positions and candidates and handle voting process via AJAX


# Route to display positions and their status
# Route to display positions and their status
@app.route('/votes')
def votes():
    if 'user' not in session:
        return redirect(url_for('signin'))
    cursor.execute(
        "SELECT positions.id, positions.description, position_time.starting_time, position_time.ending_time FROM positions LEFT JOIN position_time ON positions.id = position_time.position_id")
    positions = cursor.fetchall()

    # Calculate remaining time and determine status for each position
    for position in positions:
        if position['ending_time']:
            current_time = datetime.now()
            remaining_time = position['ending_time'] - current_time
            if remaining_time.total_seconds() > 0:
                position['remaining_time'] = remaining_time.total_seconds()
                position['status'] = 'Running'
            else:
                position['remaining_time'] = 0
                position['status'] = 'Ended'
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
    if ('user' in session):
        cursor.execute(
            "SELECT student_id, first_name, last_name, course, email, picture FROM users WHERE role = 'student'")
        student_users = cursor.fetchall()
        return render_template('voters.html', student_users=student_users)
    return redirect(url_for('signin'))


@app.route('/tally_student', methods=['GET', 'POST'])
def tally_student():
    if ('user' in session):
        # Fetch positions from the database
        cursor.execute("SELECT positions.id, positions.description FROM positions")
        positions = cursor.fetchall()

        # For each position, fetch candidates and their votes
        for position in positions:
            cursor.execute("SELECT candidates.id, candidates.first_name, candidates.last_name, COUNT(ballot.id) AS votes \
                                FROM candidates LEFT JOIN ballot ON candidates.id = ballot.candidate_id \
                                WHERE candidates.position_id = %s \
                                GROUP BY candidates.id", (position['id'],))
            position['candidates'] = cursor.fetchall()

        return render_template('tally_student.html', positions=positions)
    return redirect(url_for('signin'))


@app.route('/candidates', methods=['GET', 'POST'])
def candidates():
    if 'user' in session:
        # Fetch positions from the database
        cursor.execute("SELECT * FROM positions")
        positions = cursor.fetchall()
        # Fetch candidates from the database
        cursor.execute("SELECT * FROM candidates")
        candidates = cursor.fetchall()
        return render_template('candidates.html', positions=positions, candidates=candidates)
    return redirect(url_for('signin'))


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

        cursor.execute("SELECT id FROM positions WHERE description = %s", (position,))
        position_id = cursor.fetchone()['id']

        if 'profile' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        profile = request.files['profile']

        if profile.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        if profile and allowed_file(profile.filename):
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            _, file_extension = os.path.splitext(profile.filename)
            filename = f"{random_string}_{timestamp}{file_extension}"

            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile.save(file_path)

            insert_query = "INSERT INTO candidates (position_id, profile, first_name, last_name, student_id, position) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (position_id, filename, first_name, last_name, student_id, position))
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
    if ('user' in session):
        if request.method == 'GET':
            # Fetch positions from the database
            cursor.execute("SELECT * FROM positions")
            positions = cursor.fetchall()
            return render_template('positions.html', positions=positions)
        return redirect(url_for('signin'))
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
