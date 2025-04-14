import os
import sys
sys.path.append('C:/Users/DELL/OneDrive/Desktop/MIT/CODES/FOR GIT HUB/QR-CIP/CODE/REVIEW3/flask')
from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from base64 import b64encode
from utils.encryption import process_and_generate_shares
from io import BytesIO
import qrcode

# Load env variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")

if not SUPABASE_URL or not SUPABASE_API_KEY:
    raise ValueError("Supabase env variables not set.")

# App setup
app = Flask(__name__)
app.secret_key = SECRET_KEY
client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# QR Generator
def generate_qr_image(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf, format='PNG')
    buf.seek(0)
    return buf

# Save file to /static/
def save_qr_to_static(qr_image, filename):
    path = os.path.join(app.root_path, 'static')
    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, filename)
    with open(file_path, 'wb') as f:
        f.write(qr_image.read())
    return f"/static/{filename}"

@app.route('/')
def index():
    return redirect(url_for('login_form'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    
    username = request.form['username']
    phone = request.form['phone_number']
    password = generate_password_hash(request.form['password'])

    if client.table("users").select("*").eq("username", username).execute().data:
        return redirect(url_for('signup', message="Username already exists."))

    client.table("users").insert({
        "username": username,
        "phone": phone,
        "password_hash": password
    }).execute()

    return redirect(url_for('login_form'))

@app.route('/login', methods=['GET', 'POST'])
def login_form():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']
    result = client.table("users").select("*").eq("username", username).execute().data

    if result and check_password_hash(result[0]['password_hash'], password):
        session['username'] = username
        return redirect(url_for('dashboard'))
    return render_template('login.html', message="Invalid login.")

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login_form'))

    if request.method == 'POST':
        receiver = request.form['receiver']
        key = request.form['key']
        split_count = int(request.form['share_split_count'])

        uploaded_file = request.files['document']
        filename = secure_filename(uploaded_file.filename)
        file_content = uploaded_file.read().decode('utf-8')  # assuming it's text

        # Encrypt and generate shares
        shares, encrypted_data = process_and_generate_shares(key, file_content, split_count)

        # Create QR code from encrypted data
        qr_image = generate_qr_image(encrypted_data.hex())
        qr_filename = f"{session['username']}_qr.png"
        qr_path = save_qr_to_static(qr_image, qr_filename)

        # Insert to Supabase
        client.table("qr_images").insert({
            "username": session['username'],
            "receiver": receiver,
            "qr_image_path": qr_path,
            "encrypted_qr_data": b64encode(encrypted_data).decode('utf-8'),
            "shares": [b64encode(s).decode('utf-8') for s in shares]
        }).execute()

        return redirect(url_for('dashboard'))

    # Get received shares
    received = client.table("qr_images").select("*").eq("receiver", session['username']).execute().data
    return render_template('dashboard.html', username=session['username'], received_shares=received)

if __name__ == '__main__':
    app.run(debug=True)
