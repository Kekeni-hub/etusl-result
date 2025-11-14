# LOGIN CREDENTIALS - VERIFIED WORKING ✓

## Test Results

All login credentials have been tested and verified as **WORKING**:

| Username | Password | Status |
|----------|----------|--------|
| admin_main | Admin@2025 | ✓ WORKS |
| hod_admin | HOD@2025 | ✓ WORKS |
| dean_admin | DEAN@2025 | ✓ WORKS |
| admin | admin123 | ✓ WORKS |

## Access Points

### Django Admin Panel

- **URL**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- **Username**: admin_main, hod_admin, dean_admin, or admin
- **Passwords**: See table above

### Student Login

- **URL**: [http://127.0.0.1:8000/student/login/](http://127.0.0.1:8000/student/login/)
- Register a new student account

### Lecturer Login

- **URL**: [http://127.0.0.1:8000/lecturer/login/](http://127.0.0.1:8000/lecturer/login/)
- Register a new lecturer account

### HOD Portal

- **URL**: [http://127.0.0.1:8000/admin-hierarchy/hod/](http://127.0.0.1:8000/admin-hierarchy/hod/)
- Login with HOD credentials

### DEAN Portal

- **URL**: [http://127.0.0.1:8000/admin-hierarchy/dean/](http://127.0.0.1:8000/admin-hierarchy/dean/)
- Login with DEAN credentials

### Exam Officer

- **URL**: [http://127.0.0.1:8000/officer/](http://127.0.0.1:8000/officer/)
- Login with exam officer credentials

## Recommended Admin Accounts to Use

### Primary Admin (Full System Access)

- **Username**: admin_main
- **Password**: Admin@2025
- **Role**: System Administrator
- **Email**: `admin@etusl.edu`

### Secondary HOD Admin

- **Username**: hod_admin
- **Password**: HOD@2025
- **Role**: Head of Department
- **Email**: `hod@etusl.edu`

### DEAN Admin

- **Username**: dean_admin
- **Password**: DEAN@2025
- **Role**: Dean
- **Email**: `dean@etusl.edu`

### Legacy Admin (Still Works)

- **Username**: admin
- **Password**: admin123
- **Role**: System Administrator
- **Email**: N/A

## How to Reset a Password

If you need to reset any password:

1. Open Django admin: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
2. Login with any admin account
3. Go to: Users section
4. Click on the user you want to reset
5. Scroll to password field
6. Click "this form" link to reset password
7. Enter new password and confirm

Alternatively, use Django shell:

```bash
python manage.py shell
```

Then run:

```python
from django.contrib.auth.models import User
user = User.objects.get(username='admin_main')
user.set_password('NewPassword123')
user.save()
```

## Troubleshooting

### Issue: Login page shows but credentials don't work

**Solution**:

1. Verify you're accessing the correct URL
2. Check that server is running (should see debug messages in terminal)
3. Clear browser cookies/cache and try again
4. Verify user exists in admin panel

### Issue: Forgot password

**Solution**:

1. Access Django admin with another admin account
2. Navigate to Users
3. Find the user and reset their password
4. Use the new temporary password

### Issue: Can't access admin panel

**Solution**:

1. Verify server is running: `python manage.py runserver`
2. Check URL is exactly: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
3. Make sure port 8000 is not blocked
4. Try accessing [http://127.0.0.1:8000/](http://127.0.0.1:8000/) first to see if server responds

## Database Info

- **Database**: MySQL (etu_student_result)
- **Host**: 127.0.0.1:3306
- **User**: root
- **Password**: (no password)
- **Status**: ✓ Connected and migrated (27/27 migrations)

## Server Status

- **Server**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Status**: ✓ Running (Django 4.2.13)
- **Auto-reload**: ✓ Enabled (changes to Python files will auto-reload)
- **Debug Mode**: ✓ Enabled (shows detailed error pages)

---

**Last Tested**: November 13, 2025

**Test Status**: All credentials verified working

**Next Step**: Start using the application!
