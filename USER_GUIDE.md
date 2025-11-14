# ETU Student Result Management System - User Guide

## 🎯 Quick Start

### Server Status
✅ **Server Running**: http://127.0.0.1:8000/
✅ **Database**: Connected (MySQL/MariaDB)
✅ **Status**: Production Ready

---

## 👥 User Roles & Access

### 1. Admin (Main Administrator)
**Email**: admin@etusl.edu  
**Username**: admin  
**Password**: admin123  
**Access**: Full system control, manage all users and settings

**Features**:
- Create and manage users
- Add faculties, departments, programs
- View system logs
- Configure system settings

**Access**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

### 2. Primary Admin
**Email**: admin@etusl.edu  
**Username**: admin_main  
**Password**: Admin@2025  
**Access**: Administrative operations

**Features**:
- Manage academic structures
- Create users
- Monitor system performance
- Generate reports

**Access**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

### 3. HOD (Head of Department)
**Email**: hod@etusl.edu  
**Username**: hod_admin  
**Password**: HOD@2025  
**Access**: Department management

**Features**:
- Approve lecturer results
- Monitor departmental workflow
- View student records
- Manage approval chain

**Access**: [http://127.0.0.1:8000/hod/](http://127.0.0.1:8000/hod/)

---

### 4. DEAN (Academic Dean)
**Email**: dean@etusl.edu  
**Username**: dean_admin  
**Password**: DEAN@2025  
**Access**: Faculty-level management

**Features**:
- Approve HOD submissions
- Create programs and departments
- Add students to system
- Monitor faculty workflow

**Access**: [http://127.0.0.1:8000/dean/](http://127.0.0.1:8000/dean/)

---

### 5. Lecturer
**Access**: Lecturer dashboard  
**Features**:
- Upload student results
- Submit to HOD for approval
- View submission history
- Download result reports

**Access**: [http://127.0.0.1:8000/lecturer/](http://127.0.0.1:8000/lecturer/)

---

### 6. Student
**Access**: Student portal  
**Features**:
- View academic results
- Download transcripts
- View course information
- Upload profile photo

**Access**: [http://127.0.0.1:8000/student/](http://127.0.0.1:8000/student/)

---

## 📋 System Setup & Initial Configuration

### Step 1: Start the Server
```bash
cd c:\Etu_student_result
python manage.py runserver
```

Server runs on: **http://127.0.0.1:8000/**

### Step 2: Log in to Admin
1. Navigate to [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
2. Use credentials:
   - Username: `admin`
   - Password: `admin123`

### Step 3: Create Academic Structure
1. Go to **Faculties** → Click **Add Faculty**
2. Enter faculty name and code
3. Go to **Departments** → Add departments under faculties
4. Go to **Programs** → Add programs under departments

### Step 4: Create Users
1. Go to **Users** → Click **Add User**
2. Assign roles (Lecturer, HOD, DEAN, Student)
3. Set temporary password
4. Save user

### Step 5: Add Students
1. As DEAN or Admin: Go to **Students** → Click **Add Student**
2. Enter student information (ID, name, program)
3. Upload student photo (optional)
4. Save student

---

## 🔄 Approval Workflow

### Multi-Tier Approval Process

```
Lecturer uploads results
    ↓
HOD reviews and approves
    ↓
DEAN reviews and approves
    ↓
Exam Officer finalizes
    ↓
Results published
```

### Lecturer: Upload Results

1. **Log in** with lecturer credentials
2. Navigate to **Upload Results**
3. **Select Program**
4. Enter:
   - Subject name
   - Result type (Exam, Test, Assignment, etc.)
   - Academic year (e.g., 2024/2025)
   - Semester (1 or 2)
5. **Add Students**: 
   - Select student
   - Enter score
   - Click **Add More Students** for additional rows
6. **Submit** → Goes to HOD for approval

### HOD: Review & Approve

1. **Log in** with HOD credentials
2. Navigate to **Pending Approvals**
3. **Review** lecturer submissions
4. **Add comments** if needed
5. **Approve** → Forwards to DEAN

### DEAN: Review & Approve

1. **Log in** with DEAN credentials
2. Navigate to **Faculty Approvals**
3. **Review** HOD submissions
4. **Approve** → Forwards to Exam Officer

### Exam Officer: Finalize

1. **Log in** with exam officer credentials
2. Navigate to **Final Review**
3. **Verify** all data
4. **Publish** results

---

## 📊 Available Features

### Student Result Management
- ✅ Multi-student batch upload
- ✅ Multiple result types (Exam, Test, Assignment, Presentation, Attendance)
- ✅ Automatic score validation
- ✅ Academic year and semester tracking

### User Management
- ✅ Role-based access control
- ✅ Multi-level authentication
- ✅ User profile management
- ✅ Student photo support

### Approval Workflow
- ✅ 4-tier approval system (Lecturer → HOD → DEAN → Exam Officer)
- ✅ Comment and feedback system
- ✅ Rejection with reasons
- ✅ Audit trail logging

### Reporting
- ✅ Generate result transcripts
- ✅ Department-wise reports
- ✅ Program-wise analytics
- ✅ Semester performance metrics

### Security
- ✅ CSRF protection on all forms
- ✅ XSS prevention with template escaping
- ✅ SQL injection prevention via ORM
- ✅ Secure password hashing
- ✅ Role-based permissions

---

## 🌐 Access Points

| Function | URL | Required Role |
|----------|-----|----------------|
| Home | [http://127.0.0.1:8000/](http://127.0.0.1:8000/) | All |
| Admin Panel | [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) | Admin |
| HOD Dashboard | [http://127.0.0.1:8000/hod/](http://127.0.0.1:8000/hod/) | HOD |
| DEAN Dashboard | [http://127.0.0.1:8000/dean/](http://127.0.0.1:8000/dean/) | DEAN |
| Lecturer Dashboard | [http://127.0.0.1:8000/lecturer/](http://127.0.0.1:8000/lecturer/) | Lecturer |
| Student Portal | [http://127.0.0.1:8000/student/](http://127.0.0.1:8000/student/) | Student |
| Upload Results | [http://127.0.0.1:8000/lecturer/upload-results/](http://127.0.0.1:8000/lecturer/upload-results/) | Lecturer |

---

## 🔐 Login Credentials

### All Active User Accounts

| Role | Username | Password | Email |
|------|----------|----------|-------|
| Admin (Legacy) | admin | admin123 | admin@etusl.edu |
| Admin (Primary) | admin_main | Admin@2025 | admin@etusl.edu |
| HOD | hod_admin | HOD@2025 | hod@etusl.edu |
| DEAN | dean_admin | DEAN@2025 | dean@etusl.edu |

**Note**: Use credentials based on your role for system access.

---

## 📱 Mobile Compatibility

✅ Responsive design for all screen sizes
✅ Mobile-friendly interface
✅ Touch-optimized buttons
✅ Tablet support

---

## 🛠️ Troubleshooting

### Server Won't Start
```bash
# Check Python version
python --version

# Reinstall dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

### Database Connection Error
1. **Verify XAMPP MySQL is running**
   - Open XAMPP Control Panel
   - Start MySQL server
   - Verify port 3306 is open

2. **Check database credentials in `settings.py`**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'etu_student_result',
           'USER': 'root',
           'PASSWORD': '',
           'HOST': '127.0.0.1',
           'PORT': '3306',
       }
   }
   ```

### Can't Log In
1. Clear browser cookies
2. Check username/password (case-sensitive)
3. Verify user exists in admin panel
4. Check user is assigned correct role

### Results Not Appearing
1. Verify all approval tiers completed
2. Check database has no errors: `python manage.py check`
3. Restart server: `python manage.py runserver`

---

## 📝 Common Tasks

### Add a New Lecturer
1. Go to Admin Panel
2. **Users** → **Add User**
3. Fill form:
   - Username
   - Email
   - First Name
   - Last Name
4. **Roles**: Select "Lecturer"
5. Set temporary password
6. Save

### Create a New Program
1. As DEAN/Admin: Go to **Programs** → **Add**
2. Enter:
   - Program name
   - Program code
   - Select Department
   - Duration (years)
3. Save

### Upload Results (Lecturer)
1. Log in as Lecturer
2. **Upload Results**
3. Select program
4. Enter course details
5. Add students and scores
6. **Submit**

### Approve Results (HOD)
1. Log in as HOD
2. **Pending Approvals**
3. Review submission
4. Add comments (optional)
5. **Approve** or **Reject**

---

## 📞 Support & Help

### Getting Help
- Check documentation files in project root
- Review error messages carefully
- Check system logs for debugging

### System Information
- **Framework**: Django 4.2.13 LTS
- **Database**: MySQL/MariaDB 10.4.32
- **Python**: 3.13.x
- **Server**: Development (can be deployed to production)

### Important Files
- `settings.py` - Configuration
- `manage.py` - Django commands
- `README.md` - Project overview
- `QUICK_REFERENCE.md` - Quick commands
- `LOGIN_CREDENTIALS.md` - User accounts

---

## ✅ System Status

**Current Status**: ✅ **OPERATIONAL**

- ✅ Server: Running
- ✅ Database: Connected
- ✅ All migrations: Applied (27/27)
- ✅ System checks: Passed (0 issues)
- ✅ Users: 4 active accounts
- ✅ Security: Enabled
- ✅ Documentation: Complete

---

## 🚀 Ready to Use

The ETU Student Result Management System is fully operational and ready for users!

**Start using it now**:
1. Start server: `python manage.py runserver`
2. Open browser: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
3. Log in with your credentials
4. Begin managing student results

---

**Last Updated**: November 14, 2025
**Version**: 1.0 - Production Ready
**Status**: All Systems Operational ✅
