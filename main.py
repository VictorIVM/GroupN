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
def home():
    if 'email' in session:
        return render_template('home.html', email=session['email'])
    else:
        return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql_connection.cursor()
        cur.execute("SELECT email, password FROM voters WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and password == user[1]:
            session['email'] = user[0]
            return redirect(url_for('home'))
        else:
            return render_template("login.html", error='Invalid username or password')

    return render_template('login.html')
@app.route('/register',methods=['get','post'])
def register():
    if request.method=='POST':
        first_name= request.form['name']
        email = request.form['email']
        adm_no=request.form['admno']
        password = request.form['password']

        cur = mysql_connection.cursor()
        cur.execute("INSERT into voters (firstname, email,admno password) values ('(first_name)', '(email)', "
                    "'(admno)','(password)' )")
        cur.close()

        return render_template(url_for('loginz'))

    return render_template('registet')




if __name__ == '__main__':
    app.run(debug=True)
