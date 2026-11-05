# SETUP GUIDE

## Quick Start Instructions

### Step 1: Install Dependencies

Open a terminal/command prompt in the project directory and run:

```bash
pip install Flask Werkzeug
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

### Step 2: Run the Application

```bash
python app.py
```

The application will:
1. Automatically create the database directory
2. Initialize the database with all tables
3. Create a default admin user
4. Start the Flask development server

### Step 3: Access the System

Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

### Step 4: Login

Use these default credentials:
- **Username**: admin
- **Password**: admin123

## System Verification Checklist

After starting the system, verify:

- [ ] Login page loads correctly
- [ ] Can login with default credentials
- [ ] Dashboard displays with statistics (all zeros initially)
- [ ] Can navigate to all pages via sidebar
- [ ] Can register a new patient
- [ ] Can search for patients
- [ ] Can schedule appointments
- [ ] Can filter appointments
- [ ] Can record visits
- [ ] Visit recording updates appointment status (transaction)

## Common Issues and Solutions

### Issue: "ModuleNotFoundError: No module named 'flask'"
**Solution**: Install Flask using `pip install Flask`

### Issue: "Database file not found"
**Solution**: The database will be created automatically on first run. Ensure write permissions in the project directory.

### Issue: "Cannot connect to server"
**Solution**: Check that port 5000 is not in use. You can change the port in app.py

### Issue: "Login not working"
**Solution**: Ensure the database was initialized properly. Delete the database folder and restart the application.

## Testing the System

### Test Scenario 1: Patient Registration
1. Login to the system
2. Navigate to Patients → Register New Patient
3. Enter patient details (Name: "John Doe", Contact: "555-1234")
4. Submit the form
5. Verify patient appears in the patients list with auto-generated code (PT000001)

### Test Scenario 2: Appointment Scheduling
1. Navigate to Appointments → Schedule New Appointment
2. Select the patient you created
3. Choose tomorrow's date and a time (e.g., 10:00)
4. Add reason: "Routine checkup"
5. Submit the form
6. Verify appointment appears in appointments list with "Scheduled" status

### Test Scenario 3: Recording a Visit (Transaction Test)
1. Navigate to Visit Records → Record Visit
2. Select the patient
3. When you select the patient, the appointment dropdown should populate (AJAX)
4. Select the appointment you created
5. Enter diagnosis: "General checkup"
6. Enter notes: "Patient is in good health. All vitals normal."
7. Submit the form
8. Verify:
   - Visit was recorded
   - Appointment status changed to "Completed" (transaction worked!)
   - Visit appears in patient's visit history

### Test Scenario 4: Search and Filter
1. Register multiple patients
2. Use the search feature to find specific patients
3. Schedule appointments for different dates
4. Use the appointment filters to view specific date or status

## Production Deployment Notes

Before deploying to production:

1. **Change the secret key** in app.py:
   ```python
   app.secret_key = 'your-secure-random-key-here'
   ```

2. **Change default password** or remove the default admin user

3. **Disable debug mode** in app.py:
   ```python
   app.run(debug=False)
   ```

4. **Use a production WSGI server** (e.g., Gunicorn, uWSGI)

5. **Set up HTTPS** for secure connections

6. **Configure proper database backups**

7. **Implement additional security measures**:
   - Rate limiting
   - CSRF protection tokens
   - Content Security Policy headers
   - Regular security audits

## File Locations

- **Application**: app.py
- **Database Module**: database.py
- **Database File**: database/clinic.db (created automatically)
- **Templates**: templates/ folder
- **Styles**: static/css/style.css
- **Schema**: schema.sql

## Database Location

The SQLite database file will be created at:
```
clinic_patient_record_system/database/clinic.db
```

## Stopping the Application

Press `Ctrl+C` in the terminal where the application is running.

## Resetting the Database

To start fresh:
1. Stop the application
2. Delete the `database` folder
3. Restart the application (database will be recreated)

---

**Ready to use!** The system is fully functional and includes all required features for the academic demonstration.
