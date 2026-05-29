import mysql.connector
from mysql.connector import Error
import os

# ------------------------------------------------------------
# CONFIGURATION – Read from environment variables
# ------------------------------------------------------------
# Why: Your Docker container will inject these at runtime.
# Never hardcode secrets in the source code!
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME', 'testdb')

# Check required variables
if not all([DB_HOST, DB_USER, DB_PASSWORD]):
    raise RuntimeError("Missing required env vars: DB_HOST, DB_USER, DB_PASSWORD")

# ------------------------------------------------------------
# DATABASE SETUP: create database and table if they don't exist
# ------------------------------------------------------------
def setup_database():
    """
    Connects to MySQL server (without selecting a database),
    creates the database if missing, then creates the 'users' table.
    """
    connection = None
    try:
        # Connect to the MySQL server (no database selected)
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = connection.cursor()

        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"✅ Database '{DB_NAME}' ready")

        # Select the database
        cursor.execute(f"USE {DB_NAME}")

        # Create users table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_table_sql)
        print("✅ Table 'users' ready")

    except Error as e:
        print(f"❌ DB setup error: {e}")
        raise
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# ------------------------------------------------------------
# INSERT USER INTO RDS
# ------------------------------------------------------------
def insert_user(name, email):
    """Inserts a user into the 'users' table."""
    connection = None
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = connection.cursor()
        # Using placeholders (%s) to prevent SQL injection
        sql = "INSERT INTO users (name, email) VALUES (%s, %s)"
        cursor.execute(sql, (name, email))
        connection.commit()  # Commit the transaction
        print(f"✅ User '{name}' inserted. ID: {cursor.lastrowid}")
        return True
    except Error as e:
        print(f"❌ Insert failed: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# ------------------------------------------------------------
# FETCH AND DISPLAY ALL USERS
# ------------------------------------------------------------
def show_all_users():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = connection.cursor()
        cursor.execute("SELECT id, name, email, created_at FROM users ORDER BY created_at DESC")
        rows = cursor.fetchall()
        if not rows:
            print("📭 No users found.")
        else:
            print("\n--- Users in RDS ---")
            for row in rows:
                print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Created: {row[3]}")
            print("--------------------\n")
    except Error as e:
        print(f"❌ Fetch error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# ------------------------------------------------------------
# MAIN MENU LOOP
# ------------------------------------------------------------
def main():
    print("=== Python + RDS MySQL (Docker) ===")
    setup_database()
    show_all_users()

    while True:
        print("\nOptions:")
        print("1. Add user")
        print("2. View all users")
        print("3. Exit")
        choice = input("Choice: ")

        if choice == '1':
            name = input("Name: ").strip()
            email = input("Email: ").strip()
            if name and email:
                insert_user(name, email)
            else:
                print("Both fields required.")
        elif choice == '2':
            show_all_users()
        elif choice == '3':
            print("Bye!")
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()