# Student Result Management System

A comprehensive Django-based web application for managing student academic results. This system allows lecturers to upload results, admin to manage and publish them, and students to view their academic performance.

## Features

### Student Features
- **Secure Login** - Login with Student Name, Student ID, and Email
- **Dashboard** - View personal information and academic history
- **Result Viewing** - Browse results organized by academic year
- **PDF Download** - Download individual results for record keeping

### Lecturer Features
- **Registration & Login** - Create account and login with credentials
- **Dashboard** - Overview of uploads and status
- **Result Upload** - Upload exam records, tests, assignments, presentations, attendance
- **By Classification** - Upload results by program, department, or faculty
- **Status Tracking** - Monitor pending and published submissions

### Admin Features
- **User Management** - View and manage all users in the system
- **Faculty Management** - Create, edit, and manage faculties
- **Department Management** - Organize departments within faculties
- **Result Management** - Review, publish, or unpublish student results
- **Notifications** - Send system-wide messages to students
- **Reports** - Generate and view system reports

## System Requirements

- Python 3.8+
- Django 5.2+
- SQLite3 (default)
- Modern web browser

## Installation & Setup

### 1. Clone or Download the Project

```bash
cd c:\Etu_student_result
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install django==5.2.7
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Create Admin User and Setup Data

```bash
python manage.py shell
# Then paste the contents of setup.py or run:
exec(open('setup.py').read())
```

Or manually create using Django shell:

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Visit: `http://127.0.0.1:8000`

## Default Login Credentials

### Admin Panel
- **URL**: http://127.0.0.1:8000/officer/login/
- **Email**: admin@university.edu
- **Password**: admin123

### Student Login
- Go to: http://127.0.0.1:8000/student/login/
- Enter: Student Name, Student ID, Email

### Lecturer Portal
- Registration: http://127.0.0.1:8000/lecturer/register/
- Login: http://127.0.0.1:8000/lecturer/login/

## Project Structure

```
Etu_student_result/
├── Etu_student_result/      # Main project configuration
│   ├── settings.py          # Django settings
│   ├── urls.py              # URL routing
│   ├── wsgi.py              # WSGI application
│   └── asgi.py              # ASGI application
├── student/                 # Student app
│   ├── models.py            # Student, Result models
│   ├── views.py             # Student views
│   ├── urls.py              # Student URLs
│   └── admin.py             # Admin configuration
├── lecturer/                # Lecturer app
│   ├── models.py            # Lecturer model
│   ├── views.py             # Lecturer views
│   ├── urls.py              # Lecturer URLs
│   └── admin.py             # Admin configuration
├── exam_officer/            # Admin/Exam Officer app
│   ├── models.py            # ExamOfficer, Notification, Report models
│   ├── views.py             # Admin views
│   ├── urls.py              # Admin URLs
│   └── admin.py             # Admin configuration
├── templates/               # HTML templates
│   ├── base.html            # Base template
│   ├── home.html            # Home page
│   ├── student/             # Student templates
│   ├── lecturer/            # Lecturer templates
│   └── admin/               # Admin templates
├── static/                  # Static files
│   ├── css/
│   │   └── style.css        # Custom styles
│   ├── js/
│   │   └── script.js        # JavaScript utilities
│   └── images/
├── manage.py                # Django management script
├── setup.py                 # Database setup script
└── db.sqlite3               # SQLite database
```

## URLs

### Student URLs
- Home: `/`
- Student Login: `/student/login/`
- Student Dashboard: `/student/dashboard/`
- Download Result: `/student/download-result/<id>/`

### Lecturer URLs
- Lecturer Home: `/lecturer/`
- Register: `/lecturer/register/`
- Login: `/lecturer/login/`
- Dashboard: `/lecturer/dashboard/`
- Upload Results: `/lecturer/upload-results/`

### Admin URLs
- Admin Login: `/officer/login/`
- Dashboard: `/officer/dashboard/`
- Manage Faculties: `/officer/faculties/`
- Manage Departments: `/officer/departments/`
- Manage Results: `/officer/results/`
- Send Notifications: `/officer/notifications/`
- View Reports: `/officer/reports/`

## Database Models

### Student Models
- **Faculty**: University faculties with code and description
- **Department**: Departments within faculties
- **Program**: Programs within departments
- **Student**: Student profile with academic year tracking
- **Result**: Academic results (exams, tests, assignments, etc.)

### Lecturer Models
- **Lecturer**: Lecturer profile with faculty/department assignment

### Admin Models
- **ExamOfficer**: Admin/Exam Officer profile
- **Notification**: System notifications for users
- **SystemReport**: Generated system reports

## Features in Detail

### Student Dashboard
- View profile information
- Browse results by academic year
- Track performance through semesters
- Download results as HTML files
- See publication status of results

### Lecturer Portal
- Register and await admin verification
- Upload multiple result types
- Organize uploads by program/department
- Track submission status
- View upload history

### Admin Dashboard
- Monitor system statistics
- Manage academic structure (faculties/departments)
- Review and publish student results
- Send notifications and announcements
- Generate system reports

## Security Features

- **Authentication**: Session-based authentication for all users
- **Authorization**: Role-based access control (Student, Lecturer, Admin)
- **CSRF Protection**: Django CSRF token protection on all forms
- **Password Security**: Django password hashing and validation
- **Data Validation**: Form validation on client and server side

## Advanced Features

### Result Management
- Grade calculation based on score
- Academic year and semester organization
- Publication workflow (draft → published)
- Bulk operations support

### Notification System
- Send notifications to specific students
- Multiple notification types
- Read/unread tracking
- Timestamp recording

### Reporting
- Generate reports by faculty/department
- Report archiving
- Multiple report types

## Troubleshooting

### Database Issues
```bash
python manage.py migrate
python manage.py flush  # Clear all data
```

### Template Not Found
Ensure `templates/` directory is in project root and configured in `settings.py`

### Static Files Not Loading
```bash
python manage.py collectstatic
```

## Future Enhancements

- [ ] Email notifications integration
- [ ] Result import via CSV/Excel
- [ ] Advanced analytics and charts
- [ ] Mobile app development
- [ ] API development (REST/GraphQL)
- [ ] Document upload and storage
- [ ] Performance analytics
- [ ] GPA calculation system

## Support

For issues or questions:
1. Check the console for error messages
2. Verify database migrations have run
3. Ensure all required fields are filled in forms
4. Clear browser cache if template changes don't appear

## License

This project is provided as-is for educational purposes.

## Technologies Used

- **Backend**: Python, Django 5.2
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: SQLite3
- **Server**: Django Development Server

---

**Last Updated**: November 2025
**Version**: 1.0.0
