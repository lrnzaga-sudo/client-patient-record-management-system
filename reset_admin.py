"""
Script to reset the admin password
Run this if you're having login issues
"""
import sqlite3
import os
from werkzeug.security import generate_password_hash

# Database path
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'clinic.db')

def reset_admin_password():
    """Reset admin password to admin123"""

    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    # Connect to database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute('PRAGMA foreign_keys = ON')

    # Check if users table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if not cursor.fetchone():
        print("Database not initialized. Please run app.py first to create tables.")
        conn.close()
        return

    # Generate new password hash
    password_hash = generate_password_hash('admin123')

    # Check if admin user exists
    cursor.execute('SELECT user_id FROM users WHERE username = ?', ('admin',))
    admin = cursor.fetchone()

    if admin:
        # Update existing admin password
        cursor.execute(
            'UPDATE users SET password_hash = ? WHERE username = ?',
            (password_hash, 'admin')
        )
        print("✓ Admin password reset successfully!")
    else:
        # Create new admin user
        cursor.execute(
            'INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)',
            ('admin', password_hash, 'System Administrator', 'admin')
        )
        print("✓ Admin user created successfully!")

    conn.commit()
    conn.close()

    print("\nLogin credentials:")
    print("Username: admin")
    print("Password: admin123")

if __name__ == '__main__':
    try:
        reset_admin_password()
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have installed the required packages:")
        print("pip install Flask Werkzeug")
