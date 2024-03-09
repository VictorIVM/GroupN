import mysql.connector
from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = "my secret key"

# Configure MySQL connection
mysql_connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='voting_db'
)


@app.route('/')
def dashboard():
    if 'email' in session:
        firstname = session.get('firstname')
        return render_template('welcome.html', firstname=firstname)
    else:
        return render_template('welcome.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql_connection.cursor()
        cur.execute("SELECT firstname, password FROM voters WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and password == user[1]:
            session['email'] = email
            session['firstname'] = user[0]  # Storing the first name in session
            return redirect(url_for('dashboard'))
        else:
            return render_template("login.html", error='Invalid username or password')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = request.form['firstname']
        email = request.form['email']
        registration = request.form['registration']
        password = request.form['password']

        cur = mysql_connection.cursor()
        query = "INSERT INTO voters (`firstname`, email, registration, password) VALUES (%(first_name)s, %(email)s, %(registration)s, %(password)s)"
        data = {
            'first_name': firstname,
            'email': email,
            'registration': registration,
            'password': password
        }
        cur.execute(query, data)
        mysql_connection.commit()
        cur.close()
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return render_template('welcome.html')


if __name__ == '__main__':
    app.run(debug=True)
