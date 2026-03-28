from flask import Flask, request, jsonify, render_template, g
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)

#---------Notification Logic--------

def send_notification(title, body):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT token FROM tokens")
    rows = cursor.fetchall()

    tokens = [row[0] for row in rows if row[0]]

    for token in tokens:
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                token=token,
            )
            messaging.send(message)
        except Exception as e:
            print("Notification error for token", token, ":", e)

app = Flask(__name__)
CORS(app)

DB_NAME = "poll.db"

# ---------- DB CONNECTION ----------

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

# ---------- INIT DB ----------

def init_db():
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS polls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        purpose TEXT,
        venue TEXT,
        description TEXT,
        created_at TEXT,
        expires_at TEXT,
        status TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        poll_id INTEGER,
        user_id INTEGER,
        response TEXT,
        reason TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        token TEXT
        )
        """)

    db.commit()
    db.close()

# ---------- AUTO EXPIRE FUNCTION ----------

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
def index():
    return render_template("index.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/poll")
def poll():
    return render_template("poll.html")

@app.route("/vote-page")
def vote_page():
    return render_template("vote.html")

@app.route("/result")
def result():
    return render_template("result.html")

# ---------- AUTH ----------

@app.route("/signup-user", methods=["POST"])
def signup_user():
    data = request.json
    name = data.get("name","").strip()
    password = data.get("password","").strip()

    if not name or not password:
        return jsonify({"error":"All fields required"}),400

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users WHERE name=?", (name,))
    if cursor.fetchone():
        return jsonify({"error":"User exists"}),400

    cursor.execute("INSERT INTO users (name,password) VALUES (?,?)", (name,password))
    db.commit()

    return jsonify({"message":"Signup success"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    name = data.get("name","").strip()
    password = data.get("password","").strip()

    if not name or not password:
        return jsonify({"error":"All fields required"}),400

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id,password FROM users WHERE name=?", (name,))
    user = cursor.fetchone()

    if not user or user["password"] != password:
        return jsonify({"error":"Invalid credentials"}),401

    return jsonify({"user_id": user["id"]})

# ---------- POLL ----------

@app.route("/create-poll", methods=["POST"])
def create_poll():
    expire_polls() 

    data = request.json
    purpose = data.get("purpose","").strip()
    venue = data.get("venue","").strip()
    description = data.get("description","").strip()

    if not purpose or not venue or not description:
        return jsonify({"error":"All fields required"}),400

    db = get_db()
    cursor = db.cursor()

    # check active poll globally
    cursor.execute("""
    SELECT * FROM polls 
    WHERE status='active' AND expires_at > datetime('now')
    LIMIT 1
    """)
    poll = cursor.fetchone()

    if poll:
        return jsonify({"message":"A poll is already going on"}),400

    now = datetime.now()
    expiry = now + timedelta(hours=24)

    cursor.execute("""
    INSERT INTO polls (purpose,venue,description,created_at,expires_at,status)
    VALUES (?,?,?,?,?,'active')
    """,(purpose,venue,description,now,expiry))

    db.commit()

    return jsonify({"message":"Poll created"})
    send_notification("New Poll Live!", purpose)

@app.route("/active-poll")
def active_poll():
    expire_polls() 

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    SELECT * FROM polls 
    WHERE status='active' AND expires_at > datetime('now')
    LIMIT 1
    """)
    poll = cursor.fetchone()

    return jsonify(dict(poll) if poll else {})

@app.route("/vote", methods=["POST"])
def vote():
    expire_polls() 

    data = request.json
    poll_id = data.get("poll_id")
    user_id = data.get("user_id")
    response = data.get("response")
    reason = data.get("reason","").strip()

    if not poll_id or not user_id or response not in ["yes","no"]:
        return jsonify({"error":"Invalid data"}),400

    if response == "no" and not reason:
        return jsonify({"error":"Reason required"}),400

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM votes WHERE poll_id=? AND user_id=?", (poll_id,user_id))
    if cursor.fetchone():
        return jsonify({"error":"Already voted"}),400

    cursor.execute("""
    INSERT INTO votes (poll_id,user_id,response,reason)
    VALUES (?,?,?,?)
    """,(poll_id,user_id,response,reason))

    db.commit()

    return jsonify({"message":"Vote submitted"})

@app.route("/results/<int:poll_id>")
def results(poll_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    SELECT users.name, votes.response, votes.reason
    FROM votes JOIN users ON votes.user_id=users.id
    WHERE poll_id=?
    """,(poll_id,))

    data = cursor.fetchall()

    return jsonify([dict(row) for row in data])

@app.route("/save-token", methods=["POST"])
def save_token():
    data = request.json
    user_id = data.get("user_id")
    token = data.get("token")

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    INSERT INTO tokens (user_id, token)
    VALUES (?,?)
    """,(user_id,token))

    db.commit()

    return jsonify({"message":"Now you will receive poll related notifications!"})

# ---------- RUN ----------

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
