from flask import Flask, render_template, url_for, request, session, redirect, send_from_directory, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import Model
from werkzeug.security import generate_password_hash, check_password_hash
import os

import pyrebase


app = Flask(__name__)

# Setting up SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'secret'

db = SQLAlchemy(app)  # Moved SQLAlchemy initialization outside of the if __name__ == '__main__' block


# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    registration_number = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    course = db.Column(db.String(50))
    admin_role = db.Column(db.String(50))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Nomination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    candidate_name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    votes = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Nomination {self.candidate_name}>'


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
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password) and user.role == 'admin': # Check if the user exists and the password is correct
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
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password) and user.role == 'student': # Check if the user exists and the password is correct
            session['user'] = email  # Store user's email in session
            flash('You have been logged in!', 'success')
            return redirect(url_for('dashboard'))  # Redirect to dashboard after successful sign-in
        else:
            flash('Invalid username or password', 'error')

    return render_template('signin_student.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)  # Hash the password

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409  # HTTP status code 409 for Conflict

        role = request.form['role']
        course = request.form.get('course', None)
        admin_role = request.form.get('admin_role', None)

        # Create a new user object with the hashed password
        new_user = User(first_name=first_name, last_name=last_name, email=email, password=hashed_password, role=role,
                        course=course, admin_role=admin_role)

        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')

        return redirect(url_for('signin'))

    return render_template('sign-up.html')


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


@app.route('/candidates', methods=['GET', 'POST'])
def candidates():
    return render_template('candidates.html')


@app.route('/votes', methods=['GET', 'POST'])
def votes():
    return render_template('votes.html')


@app.route('/voters', methods=['GET', 'POST'])
def voters():
    return render_template('voters.html')


@app.route('/positions', methods=['GET', 'POST'])
def positions():
    return render_template('positions.html')


if __name__ == '__main__':
    with app.app_context():  # Ensuring the application context
        # Create the SQLite database
        db.create_all()
    app.run(debug=True)