import os
import json
import sqlite3
from flask import Flask, request, jsonify, render_template, g
from flask_cors import CORS
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, messaging

app = Flask(__name__)
CORS(app)

DB_NAME = "poll.db"


service_account_info = os.environ.get('FIREBASE_CONFIG_JSON')

if service_account_info:
    try:
        cert_dict = json.loads(service_account_info)
        cred = credentials.Certificate(cert_dict)
        firebase_admin.initialize_app(cred)
        print("Firebase initialized successfully via Environment Variable.")
    except Exception as e:
        print(f"Firebase initialization error: {e}")
else:

    try:
        cred = credentials.Certificate("firebase-key.json")
        firebase_admin.initialize_app(cred)
        print("Firebase initialized via local firebase-key.json.")
    except:
        print("WARNING: No Firebase credentials found. Notifications will not work.")

# --------- NOTIFICATION LOGIC ---------

def send_notification(title, body):

    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()
    

    cursor.execute("SELECT DISTINCT token FROM tokens")
    rows = cursor.fetchall()
    db.close()

    tokens = [row[0] for row in rows if row[0]]
    
    if not tokens:
        print("Notification skipped: No tokens in database.")
        return


    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        tokens=tokens,
    )
    
    try:
        response = messaging.send_multicast(message)
        print(f"Successfully sent {response.success_count} notifications.")
    except Exception as e:
        print(f"FCM Error: {e}")

# ---------- DATABASE HELPERS ----------

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_NAME)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        password TEXT
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS polls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        purpose TEXT,
        venue TEXT,
        description TEXT,
        created_at TEXT,
        expires_at TEXT,
        status TEXT
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        poll_id INTEGER,
        user_id INTEGER,
        response TEXT,
        reason TEXT
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        token TEXT UNIQUE
    )""")
    db.commit()
    db.close()

def expire_polls():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
    UPDATE polls 
    SET status='ended'
    WHERE expires_at <= datetime('now') AND status='active'
    """)
    db.commit()

# ---------- PAGE ROUTES ----------

@app.route("/")
def index(): return render_template("index.html")

@app.route("/signup")
def signup_page(): return render_template("signup.html")

@app.route("/dashboard")
def dashboard(): return render_template("dashboard.html")

@app.route("/poll")
def poll_page(): return render_template("poll.html")

@app.route("/vote-page")
def vote_page(): return render_template("vote.html")

@app.route("/result")
def result_page(): return render_template("result.html")

@app.route('/firebase-messaging-sw.js')
def serve_sw():
    return app.send_static_file('firebase-messaging-sw.js')

# ---------- AUTH API ----------

@app.route("/signup-user", methods=["POST"])
def signup_user():
    data = request.json
    name, password = data.get("name","").strip(), data.get("password","").strip()
    if not name or not password:
        return jsonify({"error":"All fields required"}),400
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO users (name,password) VALUES (?,?)", (name,password))
        db.commit()
        return jsonify({"message":"Signup success"})
    except sqlite3.IntegrityError:
        return jsonify({"error":"User exists"}),400

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    name, password = data.get("name","").strip(), data.get("password","").strip()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id,password FROM users WHERE name=?", (name,))
    user = cursor.fetchone()
    if not user or user["password"] != password:
        return jsonify({"error":"Invalid credentials"}),401
    return jsonify({"user_id": user["id"]})

# ---------- POLL API ----------

@app.route("/create-poll", methods=["POST"])
def create_poll():
    expire_polls() 
    data = request.json
    purpose, venue, description = data.get("purpose","").strip(), data.get("venue","").strip(), data.get("description","").strip()

    if not purpose or not venue or not description:
        return jsonify({"error":"All fields required"}),400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM polls WHERE status='active' LIMIT 1")
    if cursor.fetchone():
        return jsonify({"message":"A poll is already active!"}),400

    now = datetime.now()
    expiry = now + timedelta(hours=24)
    cursor.execute("""
    INSERT INTO polls (purpose,venue,description,created_at,expires_at,status)
    VALUES (?,?,?,?,?,'active')
    """,(purpose,venue,description,now,expiry))
    db.commit()


    send_notification("New Poll Live!", f"{purpose} at {venue}")

    return jsonify({"message":"Poll Created!"})

@app.route("/active-poll")
def active_poll():
    expire_polls() 
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM polls WHERE status='active' LIMIT 1")
    poll = cursor.fetchone()
    return jsonify(dict(poll) if poll else {})

@app.route("/vote", methods=["POST"])
def vote():
    expire_polls() 
    data = request.json
    poll_id, user_id, resp, reason = data.get("poll_id"), data.get("user_id"), data.get("response"), data.get("reason","").strip()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM votes WHERE poll_id=? AND user_id=?", (poll_id,user_id))
    if cursor.fetchone(): return jsonify({"error":"Already voted"}),400
    cursor.execute("INSERT INTO votes (poll_id,user_id,response,reason) VALUES (?,?,?,?)",(poll_id,user_id,resp,reason))
    db.commit()
    return jsonify({"message":"Vote submitted"})

@app.route("/results/<int:poll_id>")
def results(poll_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT users.name, votes.response, votes.reason FROM votes JOIN users ON votes.user_id=users.id WHERE poll_id=?",(poll_id,))
    return jsonify([dict(row) for row in cursor.fetchall()])

# ---------- NOTIFICATION TOKEN API ----------

@app.route("/save-token", methods=["POST"])
def save_token():
    data = request.json
    user_id = data.get("user_id")
    token = data.get("token")
    if not user_id or not token:
        return jsonify({"error":"Missing data"}),400
    db = get_db()
    cursor = db.cursor()

    cursor.execute("INSERT OR REPLACE INTO tokens (user_id, token) VALUES (?,?)",(user_id,token))
    db.commit()
    return jsonify({"message":"Notifications enabled!"})

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
