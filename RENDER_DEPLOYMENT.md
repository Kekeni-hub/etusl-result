# Render Deployment Guide

## Quick Start (Fix Bad Gateway Error)

### Issue: Bad Gateway (502) on Render

**Common Causes:**
1. Missing or invalid `SECRET_KEY` environment variable
2. `DATABASE_URL` not set or connection fails
3. Migrations not running
4. Port binding issue (Render uses 10000, not 8000)

### Solution: Set Environment Variables in Render

1. Go to your Render service dashboard
2. Click **Environment** tab
3. Add these variables:

```
DEBUG=False
SECRET_KEY=django-insecure-your-very-long-secret-key-here-at-least-50-chars
ALLOWED_HOSTS=your-app-name.onrender.com,etusl.onrender.com,127.0.0.1,localhost
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
DJANGO_LOG_LEVEL=INFO
```

### Important: Generate a Secure SECRET_KEY

```python
# Run this locally and copy the output
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Or use Python:
```python
import secrets
print(secrets.token_urlsafe(50))
```

---

## Database Setup on Render

### Option 1: Use Render's PostgreSQL (Recommended)

1. On your Render service, click **Add Resource** → **Database** → **PostgreSQL**
2. Create a database instance
3. Render **automatically sets `DATABASE_URL`** environment variable
4. No manual configuration needed!

### Option 2: Use External MySQL

If using external MySQL:
```
DATABASE_URL=mysql://username:password@hostname:3306/database_name
```

---

## Deployment Steps

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "fix: Render deployment configuration"
   git push origin main
   ```

2. **Connect Render to GitHub**
   - Go to https://render.com
   - New Web Service → Connect GitHub repo
   - Select `etusl-result`

3. **Configure Render Service**
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: Uses Procfile automatically
   - **Environment**: Add variables from above

4. **Deploy**
   - Click **Create Web Service**
   - Render will automatically:
     - Install dependencies
     - Run migrations
     - Collect static files
     - Start your app on port 10000

5. **Check Logs**
   - If still getting 502, click **Logs** tab in Render
   - Look for error messages like:
     - `KeyError: 'SECRET_KEY'` → Add SECRET_KEY env var
     - `connection refused` → Check DATABASE_URL
     - `No such table` → Migrations didn't run

---

## Testing Locally Before Deploying

```bash
# Set environment variables
$env:DEBUG = "False"
$env:SECRET_KEY = "test-secret-key-at-least-50-chars-very-secure"
$env:ALLOWED_HOSTS = "127.0.0.1,localhost"

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Test server
python manage.py runserver 0.0.0.0:8000
```

---

## Troubleshooting

### Error: `Bad Gateway (502)`

**Check these in order:**

1. **Missing SECRET_KEY**
   ```
   Add to Render environment: SECRET_KEY=<your-secret-key>
   ```

2. **Database not accessible**
   ```
   Verify DATABASE_URL is correct
   Test connection in Render Logs
   ```

3. **Migrations failed**
   ```
   Check Render Logs for migration errors
   May need to delete old migrations if schema changed
   ```

4. **Port binding issue**
   - Procfile must use `--bind 0.0.0.0:10000`
   - Current Procfile is configured correctly

### Error: `AttributeError: module 'logging' has no attribute 'StreamHandler'`

Update requirements.txt and redeploy.

### Error: `No such table: auth_user`

Migrations aren't running. In Render:
1. Go to **Shell** tab
2. Run: `python manage.py migrate`
3. Restart the service

---

## File Reference

- **Procfile** - Tells Render how to start the app
- **.env.example** - Template for environment variables
- **requirements.txt** - Python dependencies
- **Etu_student_result/settings.py** - Django configuration with env var support
- **build.sh** - Custom build script (optional)

---

## After Deployment

1. **Create superuser**
   ```
   Render Shell → python manage.py createsuperuser
   ```

2. **Access Django admin**
   ```
   https://your-app-name.onrender.com/admin/
   ```

3. **Upload static files** (if using S3/CDN)
   ```
   python manage.py collectstatic --noinput
   ```

---

## Production Checklist

- [ ] `DEBUG = False` in Render (via `DEBUG` env var)
- [ ] `SECRET_KEY` is secure and unique (50+ characters)
- [ ] `ALLOWED_HOSTS` includes your Render domain
- [ ] Database is configured (PostgreSQL or MySQL)
- [ ] SSL/TLS enabled (`SECURE_SSL_REDIRECT=True`)
- [ ] Migrations run successfully
- [ ] Static files collected
- [ ] Logs show no errors
- [ ] Test login and basic functionality

---

## Useful Commands

```bash
# View logs
curl https://your-app-name.onrender.com/admin/

# SSH into Render Shell
# (Available in Render dashboard under Shell tab)

# Run migrations in production
python manage.py migrate

# Create superuser in production
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

---

**Last Updated**: November 14, 2025
**For more help**: https://render.com/docs/deploy-django
