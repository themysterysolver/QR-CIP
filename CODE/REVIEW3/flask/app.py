from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
from postgrest.exceptions import APIError

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

if SUPABASE_URL is None or SUPABASE_API_KEY is None:
    raise ValueError("Supabase URL or API Key not set. Check your .env file.")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret")  # Required for sessions
client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

@app.route('/')
def index():
    return 'Welcome to the app!'

# Signup Route
@app.route('/signup', methods=['GET'])
def signup_form():
    # Get the message from URL parameters (if it exists)
    message = request.args.get('message')
    return render_template('signup.html', message=message)

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    phone_number = request.form['phone_number']
    password = request.form['password']
    hashed_password = generate_password_hash(password)

    # Check if username already exists
    try:
        existing_user = client.table("users").select("*").eq("username", username).execute().data
        if existing_user:
            return redirect(url_for('signup_form', message="Username already exists."))

        # If not, insert new user
        data = {
            "username": username,
            "phone": phone_number,
            "password_hash": hashed_password
        }

        response = client.table("users").insert(data).execute()
        return redirect(url_for('login_form'))  # Redirect to login page after signup

    except APIError as e:
        err = e.args[0]
        if isinstance(err, dict):
            error_message = err.get("message") or err.get("details") or "An error occurred."
        else:
            error_message = str(err)
        return redirect(url_for('signup_form', message=f"Signup error: {error_message}"))

# Login Route
@app.route('/login', methods=['GET'])
def login_form():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Check if the user exists
    user_data = client.table("users").select("*").eq("username", username).execute().data

    if user_data:
        # Get stored password hash from database
        stored_password_hash = user_data[0]["password_hash"]

        # Check if password is correct
        if check_password_hash(stored_password_hash, password):
            # Successful login, set session and redirect to dashboard
            session['username'] = username
            return redirect(url_for('dashboard'))  # Redirect to dashboard on successful login
        else:
            return render_template('login.html', message="Incorrect password.")
    else:
        return render_template('login.html', message="User not found.")

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    # Ensure the user is logged in (session check)
    if 'username' not in session:
        return redirect(url_for('login_form'))  # Redirect to login if not logged in
    return render_template('dashboard.html', username=session['username'])

if __name__ == '__main__':
    app.run(debug=True)
