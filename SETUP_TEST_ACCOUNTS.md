# Test Accounts (Local Development)

These are test HOD and DEAN accounts created for local development and quick testing.

- HOD (Computer Science)
  - Username: `hod_cs`
  - Email: `hod.cs@example.local`
  - Password: `HodPass123!`
  - Associated faculty/department: Science / Computer Science

- DEAN (Science)
  - Username: `dean_science`
  - Email: `dean.science@example.local`
  - Password: `DeanPass123!`
  - Associated faculty: Science

Notes:
- These accounts were created automatically for development and testing via the Django shell.
- Do NOT use these credentials in production. Change the passwords with the `manage.py changepassword <username>` command if you keep them.

Commands:

Create/ensure accounts (idempotent):

```powershell
python manage.py shell -c "from django.contrib.auth.models import User; from admin_hierarchy.models import HeadOfDepartment, DeanOfFaculty; from student.models import Faculty, Department; faculty, _ = Faculty.objects.get_or_create(name='Science', code='SCI'); department, _ = Department.objects.get_or_create(name='Computer Science', code='CS', faculty=faculty); u, created = User.objects.get_or_create(username='hod_cs', defaults={'email':'hod.cs@example.local'}); u.set_password('HodPass123!'); u.save(); HeadOfDepartment.objects.get_or_create(user=u, defaults={'hod_id':'HODCS001','email':'hod.cs@example.local','department':department,'is_active':True}); print('HOD done'); v, created = User.objects.get_or_create(username='dean_science', defaults={'email':'dean.science@example.local'}); v.set_password('DeanPass123!'); v.save(); DeanOfFaculty.objects.get_or_create(user=v, defaults={'dean_id':'DEANSCI001','email':'dean.science@example.local','faculty':faculty,'is_active':True}); print('DEAN done')"
```

Remove accounts:

```powershell
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username__in=['hod_cs','dean_science']).delete(); print('Deleted')"
```
