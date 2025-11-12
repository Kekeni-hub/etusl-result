# Quick Start Guide - Student Result Management System

## Step-by-Step Setup

### Step 1: Initial Setup
```bash
# Navigate to project directory
cd c:\Etu_student_result

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Initialize Database
```bash
# Run migrations
python manage.py migrate

# Create initial data (faculties, departments, programs, admin user)
python manage.py shell
# Then copy and paste the contents of setup.py
# Or run: exec(open('setup.py').read())
```

### Step 4: Start Development Server
```bash
python manage.py runserver
```

Server will be available at: **http://127.0.0.1:8000**

## Accessing the System

### 1. Home Page
Visit: http://127.0.0.1:8000

### 2. Admin Panel
- URL: http://127.0.0.1:8000/officer/login/
- Email: `admin@university.edu`
- Password: `admin123`

### 3. Student Login
- URL: http://127.0.0.1:8000/student/login/
- Use any student credentials (created through admin)

### 4. Lecturer Portal
- Registration: http://127.0.0.1:8000/lecturer/register/
- Login: http://127.0.0.1:8000/lecturer/login/

## Django Admin Panel
- URL: http://127.0.0.1:8000/admin/
- Username: `admin@university.edu`
- Password: `admin123`

## Creating Test Data

### Create a Student (via Django Admin)
1. Go to http://127.0.0.1:8000/admin/
2. Navigate to Students → Add Student
3. Fill in:
   - User: Create new user or select existing
   - Student ID: e.g., `STU001`
   - Email: e.g., `student@university.edu`
   - Faculty, Department, Program (select from list)
   - Current Year: 1-5

### Register a Lecturer
1. Go to http://127.0.0.1:8000/lecturer/register/
2. Fill registration form:
   - Name, Email, Lecturer ID
   - Password (must match confirmation)
   - Faculty and Department
   - Other optional fields
3. Wait for admin verification (admin can verify in Django admin)

### Create Faculty/Department (via Admin Panel)
1. Go to http://127.0.0.1:8000/officer/dashboard/
2. Click "Manage Faculties" or "Manage Departments"
3. Fill form and submit

## Common Tasks

### Uploading Results (Lecturer)
1. Login as lecturer
2. Click "Upload Results"
3. Select program and fill result details
4. Add student scores
5. Submit

### Publishing Results (Admin)
1. Go to Admin Dashboard
2. Click "Manage Results"
3. View pending results
4. Click "Publish" to make visible to students

### Viewing Results (Student)
1. Login with student credentials
2. Dashboard shows all published results
3. Click "Download PDF" to get result

### Sending Notifications (Admin)
1. Go to Admin Dashboard
2. Click "Send Notifications"
3. Select recipients and compose message
4. Send

## Troubleshooting

### "Database locked" error
```bash
# Delete database and restart
rm db.sqlite3
python manage.py migrate
```

### "TemplateDoesNotExist" error
- Ensure `templates/` folder exists in project root
- Check `TEMPLATES` setting in `settings.py`

### Port 8000 already in use
```bash
python manage.py runserver 8001  # Use different port
```

### Static files not loading
```bash
python manage.py collectstatic --noinput
```

## Directory Structure After Setup
```
Etu_student_result/
├── db.sqlite3 (created after migrate)
├── staticfiles/ (created after collectstatic)
├── venv/ (created after virtual environment)
├── templates/
├── static/
├── manage.py
├── setup.py
├── requirements.txt
├── README.md
├── QUICKSTART.md
└── ... (app directories)
```

## Next Steps

1. **Familiarize yourself** with the system by exploring all pages
2. **Create test data** (students, lecturers, results)
3. **Test workflows** (login, upload, publish, view)
4. **Customize** as needed for your institution
5. **Deploy** when ready (see Django documentation)

## Useful Django Commands

```bash
# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Make migrations
python manage.py makemigrations

# Run tests
python manage.py test

# Database shell
python manage.py dbshell

# Django shell
python manage.py shell

# Reset specific app
python manage.py migrate admin zero
```

## Performance Notes

- SQLite is suitable for development and small deployments
- For production, consider PostgreSQL or MySQL
- Use `DEBUG = False` in production settings
- Configure `ALLOWED_HOSTS` properly

## Security Reminders

1. Change default admin password immediately in production
2. Use strong passwords for all accounts
3. Update Django regularly for security patches
4. Never commit `db.sqlite3` or sensitive credentials to version control
5. Use HTTPS in production

## Support & Documentation

- Django Documentation: https://docs.djangoproject.com/
- Bootstrap Documentation: https://getbootstrap.com/docs/
- SQLite Documentation: https://www.sqlite.org/docs.html

---

Happy coding! 🎓
