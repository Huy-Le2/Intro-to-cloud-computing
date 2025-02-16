import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    username TEXT UNIQUE, 
                    password TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    email TEXT,
                    address TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Register user
@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Username already exists!"
        conn.close()
        session['username'] = username
        return redirect(url_for('user_details'))
    return render_template('register.html')

# Accept user details
@app.route('/details', methods=['GET', 'POST'])
def user_details():
    if 'username' not in session:
        return redirect(url_for('register'))
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        address = request.form['address']
        username = session['username']
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE users SET first_name=?, last_name=?, email=?, address=? WHERE username=?", 
                  (first_name, last_name, email, address, username))
        conn.commit()
        conn.close()
        return redirect(url_for('display'))
    
    return render_template('details.html')

# Display user details
@app.route('/display')
def display():
    if 'username' not in session:
        return redirect(url_for('register'))
    
    username = session['username']
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT first_name, last_name, email, address FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    
    if user:
        return render_template('display.html', user=user)
    return "User not found!"

# Re-login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['username'] = username
            return redirect(url_for('display'))
        return "Invalid credentials!"
    
    return render_template('login.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
