from flask import Flask, request, redirect, render_template, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
import google.generativeai as genai

app = Flask(__name__, template_folder='../frontend')
app.secret_key = "tes_ai_secret"

# ---------------- DATABASE PATH ---------------- #

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, '..', 'database')
os.makedirs(DB_DIR, exist_ok=True)

DB = os.path.join(DB_DIR, 'users.db')

# ---------------- GEMINI CONFIG ---------------- #

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("❌ API KEY NOT FOUND")
else:
    print("✅ API KEY LOADED")

genai.configure(api_key=API_KEY)

# ---------------- CREATE DB ---------------- #

def init_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------------- ROUTES ---------------- #

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect('/login')
    return render_template('home.html', user=session['user'])

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ---------------- SIGNUP ---------------- #

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = generate_password_hash(request.form['password'])

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    existing = cursor.fetchone()

    if existing:
        conn.close()
        return render_template('signup.html', error="❌ User already exists")

    cursor.execute(
        "INSERT INTO users (username,email,password) VALUES (?,?,?)",
        (username, email, password)
    )
    conn.commit()
    conn.close()

    return redirect('/login')

# ---------------- LOGIN ---------------- #

@app.route('/login_user', methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password']

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[3], password):
        session['user'] = user[1]
        return redirect('/home')
    else:
        return render_template('login.html', error="❌ Invalid credentials")

# ---------------- AI PAGE ---------------- #

@app.route('/ai')
def ai():
    if 'user' not in session:
        return redirect('/login')
    return render_template('ai.html')

# ---------------- AI CHAT (FIXED) ---------------- #

@app.route('/ask_ai', methods=['POST'])
def ask_ai():
    data = request.get_json()
    user_msg = data.get('msg')

    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        model = genai.GenerativeModel("gemini-1.5-flash")

        response = model.generate_content(user_msg)

        reply = response.text if response else "No response"

    except Exception as e:
        reply = f"⚠️ AI Error: {str(e)}"

    return jsonify({"reply": reply})

# ------------------------------------------------ #

if __name__ == "__main__":
    app.run(debug=True)