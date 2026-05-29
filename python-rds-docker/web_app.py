import mysql.connector
from mysql.connector import Error
import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME', 'testdb')

def get_db_connection(use_database=True):
    """Get connection. If use_database=True, connect to DB_NAME; else connect to server only."""
    config = {
        'host': DB_HOST,
        'user': DB_USER,
        'password': DB_PASSWORD
    }
    if use_database:
        config['database'] = DB_NAME
    return mysql.connector.connect(**config)

def init_db():
    """Create database and table if they don't exist."""
    # First, connect without specifying the database to create it if missing
    connection = None
    try:
        connection = get_db_connection(use_database=False)
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"✅ Database '{DB_NAME}' ensured")
        cursor.execute(f"USE {DB_NAME}")
        # Create table (with phone & address columns)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                phone VARCHAR(20),
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.commit()
        print("✅ Table 'users' ready")
    except Error as e:
        print(f"❌ DB init error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        if not name or not email:
            flash('Name and email are required.', 'warning')
            return redirect(url_for('index'))

        connection = None
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, phone, address) VALUES (%s, %s, %s, %s)",
                (name, email, phone, address)
            )
            connection.commit()
            flash(f'User {name} added successfully!', 'success')
        except Error as e:
            if 'Duplicate entry' in str(e):
                flash(f'Email {email} already exists!', 'danger')
            else:
                flash(f'Database error: {e}', 'danger')
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
        return redirect(url_for('index'))

    # GET request: fetch all users
    users = []
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id, name, email, phone, address, created_at FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
    except Error as e:
        flash(f'Error fetching users: {e}', 'danger')
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    return render_template('index.html', users=users)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)