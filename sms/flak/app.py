import os
import re
from hashlib import md5
from plistlib import Data


import now as now
import pymysql
from flask import Flask, request, render_template, flash, url_for, session

import africastalking
from flask_ngrok import run_with_ngrok
from werkzeug.security import generate_password_hash, check_password_hash

from werkzeug.utils import redirect
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = '1a2b3c4d5e'
run_with_ngrok(app)

username = os.getenv('user_name', 'esurvey')
api_key = os.getenv('api_key', 'de8fbaad2b31fde57ec236a23f26c679c7d63e4eb0c6973db514373912bfec39')

africastalking.initialize(username, api_key)
sms = africastalking.SMS
conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='', db='bulksms')
app.secret_key = 'many random bytes'

mysql = pymysql


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL

        cur = conn.cursor()

        cur.execute('SELECT * FROM accounts WHERE username = %s ', (username,))

        account = cur.fetchall()

        error = None
        if cur is None:
            error = 'Incorrect username.'
        if check_password_hash(account[0], password):
            error = 'Incorrect password.'
        # Fetch one record and return result
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True

            session['username'] = request.form['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'

    return render_template('login.html', msg='')


@app.route("/main", methods=["GET", "POST"])
def main():
    flash(session['username'])





    return render_template('index.html',  username=session['username'])


@app.route('/', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = (request.form['password'])
        _hashed_password = generate_password_hash(password)
        email = request.form['email']

        # Check if account exists using MySQL
        cur = conn.cursor()
        cur.execute('SELECT * FROM accounts WHERE username = %s', (username))
        account = cur.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cur.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, _hashed_password, email))
            conn.commit()
            msg = 'You have successfully registered!'
            return redirect(url_for('login'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


@app.route('/insert', methods=["GET", "POST"])
def insert():
    if request.method == "POST":
        flash("MESSAGE WAS SEND Successfully")

        sms_message = request.form['smsMessage']
        username = session['username']
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d')

        cur = conn.cursor()
        cur.execute("INSERT INTO  sendingsms ( username,Date, Text ) VALUES (%s,%s, %s)",
                    (username, formatted_date, sms_message))
        conn.commit()
        return redirect(url_for('main'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page

        return redirect(url_for('main'))
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/phone_list/', methods=["GET", "POST"])
def phone_list():
    session['username']
    cur = conn.cursor()
    cur.execute('SELECT * FROM phoneview WHERE username = %s', (session['username']))
    data = cur.fetchall()
    cur.close()

    return render_template('phonelist.html', phoneview=data)

@app.route('/reports/', methods=["GET", "POST"])
def reports():

    cur = conn.cursor()
    cur.execute('SELECT * FROM `totalsms')
    data = cur.fetchall()

    cur.close()

    return render_template('reports.html', totalsms=data)

@app.route('/failed_sms/', methods=["GET", "POST"])
def failed_sms():

    cur = conn.cursor()
    cur.execute('SELECT * FROM notsend_sms')
    data = cur.fetchall()

    cur.close()

    return render_template('reportlayout.html', notsend_sms=data)


@app.route('/outbox/')
def outbox():
    cur = conn.cursor()
    cur.execute("SELECT  * FROM deliveryreport")
    data = cur.fetchall()
    cur.close()

    return render_template('layout2.html', deliveryreport=data)





@app.route('/delivery_report/', methods=['GET', 'POST'])
def inbound_sms():

    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

    # Sender's phone number
    messageId = request.values.get('id')

    to_number = request.values.get('phoneNumber')

    network = request.values.get('networkCode')

    status = request.values.get('status')

    Total_cost = request.values.get('cost')

    failure_for_Reason = request.values.get('failureReason')

    print('Message received - phoneNumber: %s, status: %s, networkCode: %s ,cost: %s ,id: %s' % (
        to_number, status, network, Total_cost, messageId))
    cur = conn.cursor()
    cur.execute("INSERT INTO  deliveryreport (Time, to_number, network,status ) VALUES (%s, %s, %s, %s)",
                (formatted_date, to_number, network, status))
    conn.commit()
    return redirect(url_for('main'))

    # Print the message

    return "Delivery status reported"


@app.route('/contacts/', methods=['GET', 'POST'])
def contacts():
    # Output message if something goes wrong...
    msg = ''
    # Check if phone" POST requests exist (user submitted form)
    if request.method == 'POST' and 'phone' in request.form:
        # Create variables for easy access
        phone = request.form['phone']
        username = session['username']

        # Check if phone exists using MySQL
        cur = conn.cursor()
        cur.execute('SELECT * FROM phoneno WHERE phoneNo = %s', (phone))
        account = cur.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'phone number already exists!'


        elif not phone:
            msg = 'Please fill out the form!'
        else:
            # phone doesnt exists and the form data is valid, now insert new account into accounts table
            cur.execute('INSERT INTO phoneno(username, phoneNo )VALUES(%s, %s)', (username,phone))
            conn.commit()
            msg = 'You have successfully registered!'
            return redirect(url_for('phone_list'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('contacts.html', msg=msg)


@app.route('/profile/', methods=["GET", "POST"])
def profile():
    cur = conn.cursor()
    cur.execute('SELECT * FROM accounts WHERE username = %s', (session['username']))
    data = cur.fetchall()
    cur.close()

    return render_template('profile.html', accounts=data)


@app.route('/update', methods=['POST', 'GET'])
def update():
    if request.method == 'POST':
        id_data = Data.query.get(request.form.get('row.0'))

        email = request.form['email']
        cur = conn.cursor()
        cur.execute("""
               UPDATE accounts
               SET  email=%s
               WHERE id=%s
            """, (email, id_data))
        flash("Data Updated Successfully")
        cur.close()
        return redirect(url_for('profile'))

    @app.route('/delete/<id>/', methods=['GET'])
    def delete(id):
        flash("Record Has Been Deleted Successfully")
        cur = conn.cursor()
        cur.execute("DELETE FROM accounts WHERE id=%s", (id))
        cur.commit()
        return redirect(url_for('profile'))


if __name__ == "__main__":
    app.run(debug=True)
