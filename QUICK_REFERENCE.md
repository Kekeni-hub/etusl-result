# Quick Reference - MySQL Integration

## Status: ACTIVE ✓

**Date**: November 13, 2025

**Database**: MySQL/MariaDB 10.4.32

**Django Version**: 4.2.13 LTS

**Server**: Running on [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## Connection String

```text
mysql://root:@127.0.0.1:3306/etu_student_result
```

## Start Server

```bash
python manage.py runserver
```

## Stop Server

```bash
CTRL + BREAK (Windows PowerShell)
```

---

## Quick Admin Access

- **URL**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- **Username**: admin
- **Password**: admin123

---

## Database Commands

### Test Connection

```bash
python manage.py dbshell
SELECT VERSION();
```

### Backup

```bash
mysqldump -u root etu_student_result > backup.sql
```

### Restore

```bash
mysql -u root etu_student_result < backup.sql
```

### Reset (WARNING - Deletes all data)

```bash
python manage.py flush
python manage.py migrate
```

---

## Verify Installation

```bash
python manage.py check
```

Expected output: `System check identified no issues (0 silenced).`

---

## Django Shell

```bash
python manage.py shell
```

Example queries:

```python
from django.contrib.auth.models import User
User.objects.all()

from student.models import Student
Student.objects.count()
```

---

## Database Info

- **Host**: 127.0.0.1
- **Port**: 3306
- **Database**: etu_student_result
- **User**: root
- **Password**: (empty)
- **Charset**: utf8mb4

---

## Files Modified

1. `Etu_student_result/settings.py` - Database configuration
2. `manage.py` - PyMySQL compatibility

---

## Packages Installed

- Django 4.2.13
- mysqlclient
- mysql-connector-python
- PyMySQL

---

## Migration Status

**All 27 migrations applied successfully** ✓

---

## Troubleshooting

### MySQL Won't Connect

1. Start XAMPP MySQL service
2. Verify port 3306 available
3. Check credentials in settings.py

### Permission Denied

- Ensure `media/` and `staticfiles/` folders are writable
- Check file ownership

### Database is Locked

```bash
python manage.py migrate --run-syncdb
```

---

## Next Steps

1. ✓ Database connected
2. ✓ Server running
3. → Test the application
4. → Create test accounts
5. → Verify data persists

---

**All systems operational!**
