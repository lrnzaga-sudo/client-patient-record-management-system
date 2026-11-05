import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'clinic.db')

def get_db_connection():
    """Create a database connection with foreign key support enabled."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def init_db():
    """Initialize the database with schema."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    conn = get_db_connection()
    with open(os.path.join(os.path.dirname(__file__), 'schema.sql'), 'r') as f:
        conn.executescript(f.read())

    # Guarantee a working admin account (repairs any bad/placeholder hash)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, password_hash FROM users WHERE username = ?', ('admin',))
    row = cursor.fetchone()
    if row is None:
        cursor.execute(
            'INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)',
            ('admin', generate_password_hash('admin123'), 'System Administrator', 'admin')
        )
    else:
        try:
            ok = check_password_hash(row['password_hash'], 'admin123')
        except Exception:
            ok = False
        if not ok:
            cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?',
                           (generate_password_hash('admin123'), 'admin'))
    conn.commit()
    conn.close()

# User operations
def get_user_by_username(username):
    """Get user by username."""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

def create_user(username, password, full_name, role='staff'):
    """Create a new user."""
    conn = get_db_connection()
    password_hash = generate_password_hash(password)
    try:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)',
            (username, password_hash, full_name, role)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

# Patient operations
def generate_patient_code():
    """Generate a unique patient code."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM patients')
    count = cursor.fetchone()[0]
    conn.close()
    return f'PT{str(count + 1).zfill(6)}'

def create_patient(patient_code, name, contact, date_of_birth=None, address=None):
    """Create a new patient."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO patients (patient_code, name, contact, date_of_birth, address)
               VALUES (?, ?, ?, ?, ?)''',
            (patient_code, name, contact, date_of_birth, address)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_all_patients():
    """Get all patients."""
    conn = get_db_connection()
    patients = conn.execute(
        'SELECT * FROM patients ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    return patients

def get_patient_by_id(patient_id):
    """Get patient by ID."""
    conn = get_db_connection()
    patient = conn.execute('SELECT * FROM patients WHERE patient_id = ?', (patient_id,)).fetchone()
    conn.close()
    return patient

def search_patients(query):
    """Search patients by name or patient code."""
    conn = get_db_connection()
    search_pattern = f'%{query}%'
    patients = conn.execute(
        '''SELECT * FROM patients
           WHERE name LIKE ? OR patient_code LIKE ?
           ORDER BY name''',
        (search_pattern, search_pattern)
    ).fetchall()
    conn.close()
    return patients

def update_patient(patient_id, name, contact, date_of_birth=None, address=None):
    """Update patient information."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE patients
               SET name = ?, contact = ?, date_of_birth = ?, address = ?, updated_at = CURRENT_TIMESTAMP
               WHERE patient_id = ?''',
            (name, contact, date_of_birth, address, patient_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def delete_patient(patient_id):
    """Delete a patient."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM patients WHERE patient_id = ?', (patient_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

# Appointment operations
def create_appointment(patient_id, visit_date, time, reason=None):
    """Create a new appointment."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO appointments (patient_id, visit_date, time, reason, status)
               VALUES (?, ?, ?, ?, 'Scheduled')''',
            (patient_id, visit_date, time, reason)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_all_appointments():
    """Get all appointments with patient information."""
    conn = get_db_connection()
    appointments = conn.execute(
        '''SELECT a.*, p.name, p.patient_code
           FROM appointments a
           JOIN patients p ON a.patient_id = p.patient_id
           ORDER BY a.visit_date DESC, a.time DESC'''
    ).fetchall()
    conn.close()
    return appointments

def get_appointment_by_id(appointment_id):
    """Get appointment by ID."""
    conn = get_db_connection()
    appointment = conn.execute(
        '''SELECT a.*, p.name, p.patient_code
           FROM appointments a
           JOIN patients p ON a.patient_id = p.patient_id
           WHERE a.appointment_id = ?''',
        (appointment_id,)
    ).fetchone()
    conn.close()
    return appointment

def get_appointments_by_patient(patient_id):
    """Get all appointments for a specific patient."""
    conn = get_db_connection()
    appointments = conn.execute(
        '''SELECT * FROM appointments
           WHERE patient_id = ?
           ORDER BY visit_date DESC, time DESC''',
        (patient_id,)
    ).fetchall()
    conn.close()
    return appointments

def filter_appointments(date=None, status=None):
    """Filter appointments by date and/or status."""
    conn = get_db_connection()
    query = '''SELECT a.*, p.name, p.patient_code
               FROM appointments a
               JOIN patients p ON a.patient_id = p.patient_id
               WHERE 1=1'''
    params = []

    if date:
        query += ' AND a.visit_date = ?'
        params.append(date)

    if status:
        query += ' AND a.status = ?'
        params.append(status)

    query += ' ORDER BY a.visit_date DESC, a.time DESC'

    appointments = conn.execute(query, params).fetchall()
    conn.close()
    return appointments

def update_appointment(appointment_id, patient_id, visit_date, time, reason=None):
    """Update appointment information."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE appointments
               SET patient_id = ?, visit_date = ?, time = ?, reason = ?, updated_at = CURRENT_TIMESTAMP
               WHERE appointment_id = ?''',
            (patient_id, visit_date, time, reason, appointment_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def update_appointment_status(appointment_id, status):
    """Update appointment status."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE appointments
               SET status = ?, updated_at = CURRENT_TIMESTAMP
               WHERE appointment_id = ?''',
            (status, appointment_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def delete_appointment(appointment_id):
    """Delete an appointment."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM appointments WHERE appointment_id = ?', (appointment_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

# Visit operations
def create_visit(patient_id, visit_date, notes, diagnosis=None, appointment_id=None):
    """Create a new visit record."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO visits (patient_id, appointment_id, visit_date, notes, diagnosis)
               VALUES (?, ?, ?, ?, ?)''',
            (patient_id, appointment_id, visit_date, notes, diagnosis)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def record_visit_with_appointment(patient_id, appointment_id, visit_date, notes, diagnosis=None):
    """Record a visit and update appointment status in a transaction."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Start transaction (explicit begin)
        cursor.execute('BEGIN')

        # Insert visit record
        cursor.execute(
            '''INSERT INTO visits (patient_id, appointment_id, visit_date, notes, diagnosis)
               VALUES (?, ?, ?, ?, ?)''',
            (patient_id, appointment_id, visit_date, notes, diagnosis)
        )
        visit_id = cursor.lastrowid

        # Update appointment status to Completed
        cursor.execute(
            '''UPDATE appointments
               SET status = 'Completed', updated_at = CURRENT_TIMESTAMP
               WHERE appointment_id = ?''',
            (appointment_id,)
        )

        # Commit transaction
        conn.commit()
        return visit_id
    except Exception as e:
        # Rollback on error
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_all_visits():
    """Get all visits with patient information."""
    conn = get_db_connection()
    visits = conn.execute(
        '''SELECT v.*, p.name, p.patient_code
           FROM visits v
           JOIN patients p ON v.patient_id = p.patient_id
           ORDER BY v.visit_date DESC'''
    ).fetchall()
    conn.close()
    return visits

def get_visits_by_patient(patient_id):
    """Get all visits for a specific patient."""
    conn = get_db_connection()
    visits = conn.execute(
        '''SELECT * FROM visits
           WHERE patient_id = ?
           ORDER BY visit_date DESC''',
        (patient_id,)
    ).fetchall()
    conn.close()
    return visits

def update_visit(visit_id, notes, diagnosis=None):
    """Update visit information."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE visits
               SET notes = ?, diagnosis = ?, updated_at = CURRENT_TIMESTAMP
               WHERE visit_id = ?''',
            (notes, diagnosis, visit_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

# Dashboard statistics
def get_dashboard_stats():
    """Get statistics for dashboard."""
    conn = get_db_connection()

    # Total patients
    total_patients = conn.execute('SELECT COUNT(*) FROM patients').fetchone()[0]

    # Total appointments
    total_appointments = conn.execute('SELECT COUNT(*) FROM appointments').fetchone()[0]

    # Today's appointments
    today = datetime.now().strftime('%Y-%m-%d')
    todays_appointments = conn.execute(
        'SELECT COUNT(*) FROM appointments WHERE visit_date = ?', (today,)
    ).fetchone()[0]

    # Completed appointments
    completed = conn.execute(
        'SELECT COUNT(*) FROM appointments WHERE status = "Completed"'
    ).fetchone()[0]

    # Cancelled appointments
    cancelled = conn.execute(
        'SELECT COUNT(*) FROM appointments WHERE status = "Cancelled"'
    ).fetchone()[0]

    # Upcoming appointments (scheduled and date >= today)
    upcoming = conn.execute(
        '''SELECT COUNT(*) FROM appointments
           WHERE status = "Scheduled" AND visit_date >= ?''', (today,)
    ).fetchone()[0]

    conn.close()

    return {
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'todays_appointments': todays_appointments,
        'completed': completed,
        'cancelled': cancelled,
        'upcoming': upcoming
    }
