# SECURITY QUICK REFERENCE

Quick reference guide for common security tasks and threat prevention in the ETU Student Result Management System.

## Quick Setup Checklist

Before going to production:

- [ ] Read SECURITY_HARDENING.md
- [ ] Install recommended packages: `pip install bleach cryptography argon2-cffi`
- [ ] Set DEBUG = False in settings.py
- [ ] Generate secure SECRET_KEY
- [ ] Enable HTTPS and SSL certificates
- [ ] Configure SECURE_SSL_REDIRECT = True
- [ ] Set up security logging to file
- [ ] Test all authentication flows
- [ ] Run security middleware tests
- [ ] Review ALLOWED_HOSTS configuration

## Most Common Tasks

### 1. Validate User Input

```python
from Etu_student_result.security_utils import InputValidator

# Email validation
validator = InputValidator()
is_valid = validator.validate_email('user@example.com')

# Phone validation (10-15 digits)
is_valid = validator.validate_phone('1234567890')

# Student ID (5-20 alphanumeric)
is_valid = validator.validate_student_id('STU12345')

# Password strength check
is_valid, message = validator.validate_password('SecurePass123!')

# CSV file validation
is_valid, message = validator.validate_csv_file(uploaded_file)
```

### 2. Sanitize User Input

```python
from Etu_student_result.security_utils import InputSanitizer

sanitizer = InputSanitizer()

# Sanitize plain text (removes dangerous characters)
clean = sanitizer.sanitize_text(user_input)

# Sanitize HTML (allows safe tags like <b>, <i>, <p>)
clean = sanitizer.sanitize_html(user_html)

# Sanitize filenames (removes path traversal)
clean = sanitizer.sanitize_filename(uploaded_filename)

# Escape SQL strings
clean = sanitizer.sanitize_sql_string(user_string)
```

### 3. Check Failed Logins

```python
# All failed login attempts are logged
# View logs:
tail -f /var/log/etu_security.log | grep FAILED_LOGIN

# In Django shell:
python manage.py shell
>>> import logging
>>> logger = logging.getLogger('security')
>>> logger.warning('Check logs for FAILED_LOGIN events')
```

### 4. Handle File Uploads Safely

```python
# The FileUploadSecurityMiddleware automatically:
# - Validates file extensions (blocks .exe, .php, .sh, etc.)
# - Checks file size (max 5MB)
# - Validates MIME types
# - Sanitizes filenames

# In your view:
def upload_document(request):
    file = request.FILES['document']
    # Middleware will reject dangerous files automatically
    # If file passes, it's safe to save
    document.file.save(file.name, file)
```

## Common Threats & How They're Blocked

### SQL Injection

**Threat**: `' OR '1'='1` in form field
**Protection**:

- Django ORM uses parameterized queries
- SQLInjectionProtectionMiddleware detects patterns
- Example blocked: `SELECT * FROM users WHERE id='1 OR '1'='1'`

### XSS Attack

**Threat**: `<script>alert('hacked')</script>` in user input
**Protection**:

- Django auto-escapes template variables
- XSSProtectionMiddleware detects patterns
- InputSanitizer escapes dangerous HTML

### CSRF Attack

**Threat**: Attacker tricks user to submit form to different site
**Protection**:

- CSRF tokens required on all POST/PUT/DELETE
- SameSite=Strict cookie policy
- Origin validation

### Directory Traversal

**Threat**: `../../etc/passwd` in file path
**Protection**:

- DirectoryTraversalProtectionMiddleware blocks `..` patterns
- InputSanitizer removes path traversal characters

### Brute Force Attack

**Threat**: Many login attempts
**Protection**:

- RateLimitingMiddleware: 60 requests/minute per IP
- Failed login logging and monitoring

### Malicious File Upload

**Threat**: Upload .exe, .php, .sh files
**Protection**:

- FileUploadSecurityMiddleware validates extensions
- Maximum 5MB file size
- MIME type validation

## Security Headers Explained

| Header | Purpose | Value |
|--------|---------|-------|
| `X-Content-Type-Options` | Prevent MIME sniffing | nosniff |
| `X-Frame-Options` | Prevent clickjacking | DENY |
| `X-XSS-Protection` | XSS filter in browser | 1; mode=block |
| `Strict-Transport-Security` | Force HTTPS | max-age=31536000 |
| `Content-Security-Policy` | Control resource loading | Configured |
| `Referrer-Policy` | Control referer info | strict-origin-when-cross-origin |
| `Permissions-Policy` | Restrict browser APIs | camera, microphone, etc. |

## Logging Configuration

All security events are logged to the `security` logger:

```python
import logging
logger = logging.getLogger('security')

# Security events are logged as WARNING level
# Check logs at: python manage.py handle_syslogd or /var/log/etu_security.log
```

Monitor these events:

- `FAILED_LOGIN` - Failed authentication attempts
- `SQL_INJECTION` - SQL injection attempts detected
- `DIRECTORY_TRAVERSAL` - Path traversal attempts
- `COMMAND_INJECTION` - Shell command injection attempts
- `XSS_ATTEMPT` - Cross-site scripting attempts
- `SUSPICIOUS_USER_AGENT` - Blocked bots and scanners
- `DANGEROUS_FILE_UPLOAD` - Blocked file uploads
- `RATE_LIMIT` - Rate limit violations

## Recommended Reading

- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Web Application Security](http://www.webappsec.org/)

## Emergency Procedures

### If Suspicious Activity Detected

1. **Check Logs**: Review `/var/log/etu_security.log`
2. **Identify Threat**: Determine attack type and source IP
3. **Block Attacker**: Update firewall rules to block source IP
4. **Reset Passwords**: Force password reset for affected users
5. **Review Access**: Audit database access logs
6. **Patch Vulnerabilities**: Apply security updates if needed
7. **Monitor**: Increase monitoring for next 48 hours
8. **Document**: Create incident report for future reference

### Rate Limit Lockout

If legitimate users hit rate limit (60 req/min):

1. They'll receive "Too many requests" message
2. They need to wait ~1 minute for limit to reset
3. Contact admin if issue persists

To increase rate limit (code modification needed):

```python
# In security_middleware.py, change:
self.MAX_REQUESTS_PER_MINUTE = 120  # Increase from 60
```

---

**Last Updated**: 2025-11-14
**Status**: ACTIVE
**Review Schedule**: Weekly
