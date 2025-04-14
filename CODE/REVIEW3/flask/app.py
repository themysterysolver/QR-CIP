from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os
from postgrest.exceptions import APIError

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

# Validate Supabase environment variables
if SUPABASE_URL is None or SUPABASE_API_KEY is None:
    raise ValueError("Supabase URL or API Key not set. Check your .env file.")

app = Flask(__name__)
client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

@app.route('/')
def index():
    return 'Welcome to the app!'

@app.route('/signup', methods=['GET'])
def signup_form():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    phone_number = request.form['phone_number']
    password = request.form['password']
    hashed_password = generate_password_hash(password)

    data = {
        "username": username,
        "phone": phone_number,
        "password_hash": hashed_password
    }

    try:
        response = client.table("users").insert(data).execute()
        return redirect(url_for('index'))  # Success

    except APIError as e:
        # Defensive parsing of error
        err = e.args[0]
        if isinstance(err, dict):
            error_message = err.get("message") or err.get("details") or "An error occurred."
        else:
            error_message = str(err)

        return f"Signup Error: {error_message}"

if __name__ == '__main__':
    app.run(debug=True)
