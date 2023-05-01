import binascii
import os
from urllib import response
from authy.api import AuthyApiClient

from flask import Flask, render_template, request, jsonify, redirect, url_for, session

import hashlib


import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# create a connection to the MySQL server


app.config.from_object('config')
app.secret_key = app.config['SECRET_KEY']

api = AuthyApiClient(app.config['AUTHY_API_KEY'])


@app.route("/phone_verification", methods=["GET", "POST"])
def phone_verification():
    if request.method == "POST":
        country_code = request.form.get("country_code")
        phone_number = request.form.get("phone_number")
        method = request.form.get("method")

        session['country_code'] = country_code
        session['phone_number'] = phone_number

        api.phones.verification_start(phone_number, country_code, via=method)

        return redirect(url_for("verify"))

    return render_template("phone_verification.html")


@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
            token = request.form.get("token")

            phone_number = session.get("phone_number")
            country_code = session.get("country_code")

            verification = api.phones.verification_check(phone_number, country_code, token)

            if verification.ok():
                return render_template("verifysuccess.html")

    return render_template("verify.html")

try:
    conn = mysql.connector.connect(
        host='data base host',
        database='data base name',
        user='data base user',
        password='data base password'
    )

    connection = conn # Assign the connection to the connection variable
    
    if conn.is_connected():
        print('Connected to MySQL database')

    # create the users table
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)
    print("Users table created")

except Error as e:
    print(e)



def hash_password(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    hashed_password = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    hashed_password = binascii.hexlify(hashed_password)
    return (salt + hashed_password).decode('ascii')


def insert_user_data(email, password):
    hashed_password = hash_password(password)
    try:
        cursor = conn.cursor()
        sql_query = "INSERT INTO users (email, password) VALUES (%s, %s)"
        values = (email, hashed_password)
        cursor.execute(sql_query, values)
        conn.commit()
        cursor.close()
        print('Data saved to MySQL database')
    except Error as e:
        print(f"Error inserting data into MySQL table: {e}")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email-input']
        password = request.form['password-input']
    
        insert_user_data(email, password)

        # Option 4: Redirect to the homepage after registration
        return redirect('/success')

    return render_template('success.html')

@app.route('/login1', methods=['POST'])
def login1():
    email = request.form['email-input']
    password = request.form['password-input']
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE email=%s"
    cursor.execute(query, (email,))
    user = cursor.fetchone()
    if user is None:
        # Invalid login
        return redirect('/error')
    else:
        hashed_password = user[2]
        salt = hashed_password[:64]
        hashed_password = hashed_password[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt.encode('ascii'), 100000)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        if pwdhash == hashed_password:
            # Successful login
            return redirect('/loginsuccess')
        else:
            # Invalid login
            return redirect('/error')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/success')
def success():
    return(render_template("success.html"))

@app.route('/login')
def login():
    return(render_template("login.html"))

@app.route('/error')
def error():
    return(render_template("error.html"))

@app.route('/loginsuccess')
def loginsuccess():
    return(render_template("loginsuccess.html"))


@app.route('/run')
def phone():
    return(render_template("phone_verification.html"))


if __name__ == '__main__':
    app.run(debug=True)
