# Clinic Patient Record Management System

A comprehensive web-based system for managing patient profiles, clinic appointments, and consultation records. Built with Python, Flask, and SQLite for academic demonstration purposes.

## Features

### Authentication & Authorization
- Secure login system with session-based authentication
- Password hashing using Werkzeug security
- Protected routes requiring authentication
- Logout functionality

### Patient Management
- Register new patients with unique patient codes
- View all registered patients
- Search patients by name or patient code
- View detailed patient profiles
- Edit patient information
- Delete patient records (with cascade deletion of appointments and visits)
- Auto-generated unique patient codes (PT000001, PT000002, etc.)

### Appointment Management
- Schedule new appointments for existing patients
- View all appointments
- Filter appointments by date and/or status
- Edit appointment details
- Cancel appointments
- Three status types: Scheduled, Completed, Cancelled
- Link appointments to patient records

### Clinic Visit Management
- Record consultation visits
- Link visits to appointments (optional)
- Transaction-based visit recording with automatic appointment status update
- Record consultation notes and diagnosis
- View visit history by patient or all visits
- Timeline view for patient visit history

### Dashboard
- Total patients count
- Total appointments count
- Today's appointments
- Completed appointments count
- Cancelled appointments count
- Upcoming appointments count
- Quick action buttons

### Patient History
- Complete patient profile information
- Appointment history with status tracking
- Consultation history with timeline view
- Chronologically organized records

## Technology Stack

- **Backend**: Python 3.x, Flask 3.0.0
- **Database**: SQLite with foreign key enforcement
- **Frontend**: HTML5, CSS3
- **Security**: Werkzeug password hashing
- **Session Management**: Flask sessions

## Design System

The application features a medical-focused design system:

- **Color Palette**: Clinical white backgrounds with medical blue accents, vital green for success states, alert red for warnings
- **Typography**: System font stack optimized for data-dense interfaces with tabular figures
- **Layout**: Left-aligned content with clear information hierarchy
- **Components**: Clean tables, forms with top-aligned labels, status badges, timeline views

## Database Structure

### Tables

1. **users**
   - user_id (PRIMARY KEY)
   - username (UNIQUE)
   - password_hash
   - full_name
   - role
   - created_at

2. **patients**
   - patient_id (PRIMARY KEY)
   - patient_code (UNIQUE)
   - name
   - contact
   - date_of_birth
   - address
   - created_at
   - updated_at

3. **appointments**
   - appointment_id (PRIMARY KEY)
   - patient_id (FOREIGN KEY)
   - visit_date
   - time
   - status (CHECK: Scheduled, Completed, Cancelled)
   - reason
   - created_at
   - updated_at

4. **visits**
   - visit_id (PRIMARY KEY)
   - patient_id (FOREIGN KEY)
   - appointment_id (FOREIGN KEY, nullable)
   - visit_date
   - notes
   - diagnosis
   - created_at
   - updated_at

### Database Features

- Foreign key enforcement enabled
- Cascade deletion for patient records
- Unique constraints on patient codes
- Check constraints for appointment status
- Indexes for optimized queries

## Installation & Setup

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation Steps

1. **Extract the system files**
   ```bash
   cd clinic_patient_record_system
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   The database will be automatically created on first run. The system will:
   - Create the database directory
   - Execute schema.sql to create tables
   - Insert the default admin user

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## Default Login Credentials

- **Username**: admin
- **Password**: admin123

**Important**: Change the default password in a production environment.

## Usage Guide

### Getting Started

1. **Login** with the default credentials
2. **Register patients** from the Dashboard or Patients page
3. **Schedule appointments** for registered patients
4. **Record visits** after consultations (optionally link to appointments)

### Workflow Examples

#### Registering a New Patient
1. Navigate to Patients → Register New Patient
2. Fill in required fields (Name is required)
3. Patient code is auto-generated
4. Click "Register Patient"

#### Scheduling an Appointment
1. Navigate to Appointments → Schedule New Appointment
2. Select a patient from the dropdown
3. Choose date and time
4. Add reason for visit (optional)
5. Click "Schedule Appointment"

#### Recording a Visit
1. Navigate to Visit Records → Record Visit
2. Select a patient
3. Optionally select a related appointment (auto-populates from patient's scheduled appointments)
4. Enter visit date, diagnosis, and notes
5. Click "Record Visit"
6. If linked to an appointment, the appointment status automatically updates to "Completed"

### Search and Filter

- **Search Patients**: Use the search bar on the Patients page to find by name or patient code
- **Filter Appointments**: Use date and status filters on the Appointments page

## Business Rules Implementation

1. ✅ Patient codes are unique (database constraint)
2. ✅ Authentication required for all patient record access
3. ✅ Fictional patient information only (academic system)
4. ✅ Visit records reference valid patients (foreign key)
5. ✅ Appointment records reference valid patients (foreign key)
6. ✅ Appointment status constrained to valid values (CHECK constraint)
7. ✅ Cancelled appointments tracked separately
8. ✅ Transaction-based visit recording with appointment status update
9. ✅ Rollback on transaction failure
10. ✅ Input validation before database operations

## Technical Requirements Met

✅ Five+ functional pages (11 pages total)
✅ Full CRUD operations for patients, appointments, and visits
✅ Three related database tables with foreign keys
✅ Search and filtering functionality
✅ Transaction beyond basic CRUD (visit recording with appointment update)
✅ Parameterized SQL queries (all queries use placeholders)
✅ Input validation (server-side validation for all forms)
✅ Error handling (try-catch blocks and user feedback)
✅ Success and error messages (Flash messages)
✅ Clear navigation (sidebar with active states)
✅ Authentication and authorization (login_required decorator)
✅ Complete HTML → Flask → Python → SQL → SQLite communication

## Security Features

- Password hashing with Werkzeug security
- Session-based authentication
- Protected routes with login_required decorator
- Parameterized SQL queries (prevents SQL injection)
- Input validation and sanitization
- CSRF protection through POST methods
- Secure session management

## File Structure

```
clinic_patient_record_system/
├── app.py                      # Main Flask application
├── database.py                 # Database operations
├── schema.sql                  # Database schema
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── templates/                  # HTML templates
│   ├── base.html              # Base template with navigation
│   ├── login.html             # Login page
│   ├── dashboard.html         # Dashboard with statistics
│   ├── patients.html          # Patient list with search
│   ├── patient_form.html      # Register/Edit patient form
│   ├── patient_details.html   # Patient profile and history
│   ├── appointments.html      # Appointment list with filters
│   ├── appointment_form.html  # Schedule/Edit appointment form
│   ├── record_visit.html      # Record visit form with AJAX
│   └── visit_history.html     # Visit records list/timeline
├── static/
│   └── css/
│       └── style.css          # Complete styling system
└── database/
    └── clinic.db              # SQLite database (created on first run)
```

## Pages Overview

1. **Login** - Authentication page
2. **Dashboard** - Statistics and quick actions
3. **Patients** - List all patients with search
4. **Register Patient** - Add new patient
5. **Edit Patient** - Update patient information
6. **Patient Details** - Complete patient profile with history
7. **Appointments** - List appointments with filters
8. **Schedule Appointment** - Create new appointment
9. **Edit Appointment** - Modify appointment details
10. **Record Visit** - Document consultation with transaction
11. **Visit History** - All visits or patient-specific timeline

## API Endpoints

- `GET /api/patient/<patient_id>/appointments` - Fetch patient's scheduled appointments (for AJAX in record visit form)

## Validation Rules

### Patient Registration
- Name: Required, minimum 2 characters
- Contact: Optional, must contain only valid phone characters
- Date of Birth: Optional, valid date format
- Address: Optional

### Appointment Scheduling
- Patient: Required selection
- Visit Date: Required, valid date format
- Time: Required, valid time format (HH:MM)
- Reason: Optional

### Visit Recording
- Patient: Required selection
- Visit Date: Required
- Notes: Required, minimum 5 characters
- Diagnosis: Optional
- Appointment: Optional (links visit to appointment)

## Transaction Example

When recording a visit linked to an appointment:

1. BEGIN transaction
2. INSERT visit record
3. UPDATE appointment status to 'Completed'
4. COMMIT transaction
5. If any step fails, ROLLBACK all changes

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Responsive design for mobile devices
- Progressive enhancement approach

## Future Enhancements

Potential features for expansion:
- User registration and role management
- Patient medical history tracking
- Prescription management
- Appointment reminders
- Reporting and analytics
- Export functionality (PDF/CSV)
- Multi-clinic support
- Appointment scheduling calendar view

## Troubleshooting

### Database Not Creating
- Check write permissions in the application directory
- Ensure schema.sql file exists and is readable

### Login Issues
- Verify database was initialized properly
- Check that default user was created
- Ensure session secret key is set

### Import Errors
- Verify all dependencies are installed
- Check Python version (3.7+)
- Activate virtual environment if using one

## Academic Use

This system is designed for academic demonstration purposes:
- Use only fictional patient data
- Not intended for production medical use
- Demonstrates fundamental web application concepts
- Implements best practices for security and data management

## License

This project is created for academic purposes. Feel free to use and modify for educational projects.

## Support

For issues or questions about this academic project, refer to the source code comments and this documentation.

---

**Developed as an academic demonstration of:**
- Python/Flask web development
- SQLite database design and implementation
- HTML5/CSS3 frontend development
- Secure authentication systems
- CRUD operations and transactions
- Input validation and error handling
- Responsive web design principles
