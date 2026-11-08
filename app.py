from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from functools import wraps
from datetime import datetime, date
import database as db
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'  # Change this in production

# Initialize database
db.init_db()

@app.after_request
def prevent_auth_page_caching(response):
    if request.endpoint in {'login', 'logout'}:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Input validation functions
def validate_patient_data(name, contact):
    """Validate patient registration data."""
    errors = []

    if not name or len(name.strip()) < 2:
        errors.append('Patient name must be at least 2 characters.')

    if contact and not re.match(r'^[\d\s\-\+\(\)]+$', contact):
        errors.append('Contact number contains invalid characters.')

    return errors

def find_patient_in_list(patients_list, patient_id):
    if not patient_id:
        return None
    return next(
        (patient for patient in patients_list
         if str(patient['patient_id']) == str(patient_id)),
        None
    )

def validate_appointment_data(patient_id, visit_date, time, allow_existing_date=None):
    """Validate appointment data."""
    errors = []

    if not patient_id:
        errors.append('Please select a patient.')

    if not visit_date:
        errors.append('Visit date is required.')
    else:
        try:
            date_obj = datetime.strptime(visit_date, '%Y-%m-%d')
            if date_obj.date() < date.today() and visit_date != allow_existing_date:
                errors.append('Appointment date cannot be in the past.')
        except ValueError:
            errors.append('Invalid date format.')

    if not time:
        errors.append('Time is required.')
    else:
        if not re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', time):
            errors.append('Invalid time format.')

    return errors

def validate_visit_data(patient_id, visit_date, notes):
    """Validate visit data."""
    errors = []

    if not patient_id:
        errors.append('Please select a patient.')

    if not visit_date:
        errors.append('Visit date is required.')

    if not notes or len(notes.strip()) < 5:
        errors.append('Visit notes must be at least 5 characters.')

    return errors

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('login.html')

        user = db.get_user_by_username(username)

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    stats = db.get_dashboard_stats()
    return render_template('dashboard.html', stats=stats)

# Patient routes
@app.route('/patients')
@login_required
def patients():
    search_query = request.args.get('search', '').strip()

    if search_query:
        patients_list = db.search_patients(search_query)
    else:
        patients_list = db.get_all_patients()

    return render_template('patients.html', patients=patients_list, search_query=search_query)

@app.route('/patients/register', methods=['GET', 'POST'])
@login_required
def register_patient():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        contact = request.form.get('contact', '').strip()
        date_of_birth = request.form.get('date_of_birth', '').strip()
        address = request.form.get('address', '').strip()

        # Validate input
        errors = validate_patient_data(name, contact)

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('patient_form.html', action='register', patient=None)

        # Generate patient code
        patient_code = db.generate_patient_code()

        # Create patient
        patient_id = db.create_patient(
            patient_code, name, contact,
            date_of_birth if date_of_birth else None,
            address if address else None
        )

        if patient_id:
            flash(f'Patient {name} registered successfully with code {patient_code}.', 'success')
            return redirect(url_for('patient_details', patient_id=patient_id))
        else:
            flash('Failed to register patient. Patient code may already exist.', 'error')

    return render_template('patient_form.html', action='register', patient=None)

@app.route('/patients/<int:patient_id>')
@login_required
def patient_details(patient_id):
    patient = db.get_patient_by_id(patient_id)

    if not patient:
        flash('Patient not found.', 'error')
        return redirect(url_for('patients'))

    appointments = db.get_appointments_by_patient(patient_id)
    visits = db.get_visits_by_patient(patient_id)

    return render_template('patient_details.html', patient=patient, appointments=appointments, visits=visits)

@app.route('/patients/<int:patient_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    patient = db.get_patient_by_id(patient_id)

    if not patient:
        flash('Patient not found.', 'error')
        return redirect(url_for('patients'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        contact = request.form.get('contact', '').strip()
        date_of_birth = request.form.get('date_of_birth', '').strip()
        address = request.form.get('address', '').strip()

        # Validate input
        errors = validate_patient_data(name, contact)

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('patient_form.html', action='edit', patient=patient)

        # Update patient
        success = db.update_patient(
            patient_id, name, contact,
            date_of_birth if date_of_birth else None,
            address if address else None
        )

        if success:
            flash(f'Patient {name} updated successfully.', 'success')
            return redirect(url_for('patient_details', patient_id=patient_id))
        else:
            flash('Failed to update patient.', 'error')

    return render_template('patient_form.html', action='edit', patient=patient)

@app.route('/patients/<int:patient_id>/delete', methods=['POST'])
@login_required
def delete_patient(patient_id):
    patient = db.get_patient_by_id(patient_id)

    if not patient:
        flash('Patient not found.', 'error')
        return redirect(url_for('patients'))

    success = db.delete_patient(patient_id)

    if success:
        flash(f'Patient {patient["name"]} deleted successfully.', 'success')
    else:
        flash('Failed to delete patient.', 'error')

    return redirect(url_for('patients'))

# Appointment routes
@app.route('/appointments')
@login_required
def appointments():
    filter_date = request.args.get('date', '').strip()
    filter_status = request.args.get('status', '').strip()

    if filter_date or filter_status:
        appointments_list = db.filter_appointments(
            date=filter_date if filter_date else None,
            status=filter_status if filter_status else None
        )
    else:
        appointments_list = db.get_all_appointments()

    return render_template('appointments.html', appointments=appointments_list,
                         filter_date=filter_date, filter_status=filter_status)

@app.route('/appointments/schedule', methods=['GET', 'POST'])
@login_required
def schedule_appointment():
    today = date.today().isoformat()
    selected_patient_id = request.args.get('patient_id', '').strip()
    if request.method == 'POST':
        patient_id = request.form.get('patient_id', '').strip()
        selected_patient_id = patient_id
        visit_date = request.form.get('visit_date', '').strip()
        time = request.form.get('time', '').strip()
        reason = request.form.get('reason', '').strip()

        # Validate input
        errors = validate_appointment_data(patient_id, visit_date, time)

        if errors:
            for error in errors:
                flash(error, 'error')
            patients_list = db.get_all_patients()
            selected_patient = find_patient_in_list(patients_list, selected_patient_id)
            return render_template('appointment_form.html', action='schedule',
                                 appointment=None, patients=patients_list, today=today,
                                 selected_patient_id=selected_patient_id,
                                 selected_patient=selected_patient)

        # Create appointment
        appointment_id = db.create_appointment(
            int(patient_id), visit_date, time,
            reason if reason else None
        )

        if appointment_id:
            flash('Appointment scheduled successfully.', 'success')
            return redirect(url_for('appointments'))
        else:
            flash('Failed to schedule appointment.', 'error')

    patients_list = db.get_all_patients()
    selected_patient = find_patient_in_list(patients_list, selected_patient_id)
    return render_template('appointment_form.html', action='schedule',
                         appointment=None, patients=patients_list, today=today,
                         selected_patient_id=selected_patient_id,
                         selected_patient=selected_patient)

@app.route('/appointments/<int:appointment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_appointment(appointment_id):
    today = date.today().isoformat()
    appointment = db.get_appointment_by_id(appointment_id)

    if not appointment:
        flash('Appointment not found.', 'error')
        return redirect(url_for('appointments'))

    if request.method == 'POST':
        patient_id = request.form.get('patient_id', '').strip()
        visit_date = request.form.get('visit_date', '').strip()
        time = request.form.get('time', '').strip()
        reason = request.form.get('reason', '').strip()

        # Validate input
        errors = validate_appointment_data(
            patient_id, visit_date, time,
            allow_existing_date=appointment['visit_date']
        )

        if errors:
            for error in errors:
                flash(error, 'error')
            patients_list = db.get_all_patients()
            return render_template('appointment_form.html', action='edit',
                                 appointment=appointment, patients=patients_list, today=today)

        # Update appointment
        success = db.update_appointment(
            appointment_id, int(patient_id), visit_date, time,
            reason if reason else None
        )

        if success:
            flash('Appointment updated successfully.', 'success')
            return redirect(url_for('appointments'))
        else:
            flash('Failed to update appointment.', 'error')

    patients_list = db.get_all_patients()
    return render_template('appointment_form.html', action='edit',
                         appointment=appointment, patients=patients_list, today=today)

@app.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    success = db.update_appointment_status(appointment_id, 'Cancelled')

    if success:
        flash('Appointment cancelled successfully.', 'success')
    else:
        flash('Failed to cancel appointment.', 'error')

    return redirect(url_for('appointments'))

@app.route('/appointments/<int:appointment_id>/complete', methods=['POST'])
@login_required
def complete_appointment(appointment_id):
    appointment = db.get_appointment_by_id(appointment_id)

    if not appointment:
        flash('Appointment not found.', 'error')
    elif appointment['status'] != 'Scheduled':
        flash('Only scheduled appointments can be marked as completed.', 'error')
    elif db.update_appointment_status(appointment_id, 'Completed'):
        flash('Appointment marked as completed.', 'success')
    else:
        flash('Failed to mark appointment as completed.', 'error')

    return redirect(url_for('appointments'))

# Visit routes
@app.route('/visits')
@login_required
def visits():
    visits_list = db.get_all_visits()
    return render_template('visit_history.html', visits=visits_list, patient=None)

@app.route('/visits/record', methods=['GET', 'POST'])
@login_required
def record_visit():
    selected_patient_id = request.args.get('patient_id', '').strip()
    if request.method == 'POST':
        patient_id = request.form.get('patient_id', '').strip()
        selected_patient_id = patient_id
        appointment_id = request.form.get('appointment_id', '').strip()
        visit_date = request.form.get('visit_date', '').strip()
        notes = request.form.get('notes', '').strip()
        diagnosis = request.form.get('diagnosis', '').strip()

        # Validate input
        errors = validate_visit_data(patient_id, visit_date, notes)

        if errors:
            for error in errors:
                flash(error, 'error')
            patients_list = db.get_all_patients()
            selected_patient = find_patient_in_list(patients_list, selected_patient_id)
            return render_template('record_visit.html', patients=patients_list,
                                   selected_patient_id=selected_patient_id,
                                   selected_patient=selected_patient)

        try:
            # Use transaction if appointment_id is provided
            if appointment_id and appointment_id != '':
                visit_id = db.record_visit_with_appointment(
                    int(patient_id), int(appointment_id), visit_date, notes,
                    diagnosis if diagnosis else None
                )
            else:
                visit_id = db.create_visit(
                    int(patient_id), visit_date, notes,
                    diagnosis if diagnosis else None
                )

            if visit_id:
                flash('Visit recorded successfully.', 'success')
                return redirect(url_for('patient_details', patient_id=patient_id))
            else:
                flash('Failed to record visit.', 'error')
        except Exception as e:
            flash(f'Transaction failed: {str(e)}', 'error')

    patients_list = db.get_all_patients()
    selected_patient = find_patient_in_list(patients_list, selected_patient_id)
    return render_template('record_visit.html', patients=patients_list,
                           selected_patient_id=selected_patient_id,
                           selected_patient=selected_patient)

@app.route('/patients/<int:patient_id>/visits')
@login_required
def patient_visits(patient_id):
    patient = db.get_patient_by_id(patient_id)

    if not patient:
        flash('Patient not found.', 'error')
        return redirect(url_for('patients'))

    visits_list = db.get_visits_by_patient(patient_id)
    return render_template('visit_history.html', visits=visits_list, patient=patient)

# AJAX endpoint to get appointments for a patient
@app.route('/api/patient/<int:patient_id>/appointments')
@login_required
def get_patient_appointments(patient_id):
    appointments = db.get_appointments_by_patient(patient_id)
    # Return only scheduled appointments
    scheduled = [a for a in appointments if a['status'] == 'Scheduled']
    return {'appointments': [dict(a) for a in scheduled]}

if __name__ == '__main__':
    app.run(debug=True)
