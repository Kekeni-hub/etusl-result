"""
Security utility functions for input validation, sanitization, and protection.
Implements best practices for:
- Input validation and sanitization
- Output escaping
- Password strength validation
- Data encryption
"""

import re
import hashlib
import hmac
from django.utils.html import escape
from django.utils.text import slugify
import logging

# Optional imports
try:
    from bleach import clean as bleach_clean  # type: ignore
    HAS_BLEACH = True
except ImportError:
    HAS_BLEACH = False
    bleach_clean = None

try:
    from cryptography.fernet import Fernet, InvalidToken  # type: ignore
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False

logger = logging.getLogger('security')


class InputValidator:
    """Validate various types of user input."""
    
    @staticmethod
    def validate_email(email):
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number format."""
        phone = re.sub(r'\D', '', phone)
        return 10 <= len(phone) <= 15
    
    @staticmethod
    def validate_student_id(student_id):
        """Validate student ID format."""
        # Student ID should be alphanumeric, length 5-20
        pattern = r'^[A-Z0-9]{5,20}$'
        return re.match(pattern, student_id, re.IGNORECASE) is not None
    
    @staticmethod
    def validate_username(username):
        """Validate username format."""
        # Alphanumeric, underscores, hyphens, 3-30 chars
        pattern = r'^[a-zA-Z0-9_-]{3,30}$'
        return re.match(pattern, username) is not None
    
    @staticmethod
    def validate_password_strength(password):
        """
        Validate password strength.
        Requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long."
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter."
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter."
        
        if not re.search(r'[0-9]', password):
            return False, "Password must contain at least one digit."
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
            return False, "Password must contain at least one special character."
        
        return True, "Password is strong."
    
    @staticmethod
    def validate_file_extension(filename, allowed_extensions):
        """Validate file extension."""
        filename = filename.lower()
        for ext in allowed_extensions:
            if filename.endswith(ext.lower()):
                return True
        return False
    
    @staticmethod
    def validate_csv_file(file_obj):
        """Validate CSV file format and content."""
        try:
            # Check file extension
            if not file_obj.name.lower().endswith('.csv'):
                return False, "File must be a CSV file."
            
            # Check file size (5MB max)
            if file_obj.size > 5242880:
                return False, "File size exceeds maximum limit (5MB)."
            
            # Check MIME type
            if file_obj.content_type not in ['text/csv', 'application/vnd.ms-excel', 'text/plain']:
                return False, "Invalid CSV file format."
            
            return True, "CSV file is valid."
        except Exception as e:
            logger.error(f"CSV validation error: {str(e)}")
            return False, "Error validating CSV file."


class InputSanitizer:
    """Sanitize user input to prevent injection attacks."""
    
    @staticmethod
    def sanitize_text(text, max_length=500):
        """Sanitize plain text input."""
        if not text:
            return ""
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # HTML escape
        text = escape(text)
        
        # Truncate
        text = text[:max_length]
        
        return text
    
    @staticmethod
    def sanitize_html(html, allowed_tags=None, allowed_attributes=None):
        """Sanitize HTML content allowing only safe tags."""
        if not html:
            return ""
        
        if not HAS_BLEACH:
            # Fallback to HTML escaping if bleach is not available
            logger.warning("bleach not installed, using basic HTML escaping")
            return escape(html)
        
        if not allowed_tags:
            allowed_tags = [
                'p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li',
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'code'
            ]
        
        if not allowed_attributes:
            allowed_attributes = {'a': ['href', 'title']}
        
        return bleach_clean(
            html,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
    
    @staticmethod
    def sanitize_sql_string(value):
        """Escape SQL-dangerous characters."""
        if not value:
            return ""
        
        # This should NOT be used as primary defense against SQL injection
        # Always use parameterized queries instead
        replacements = {
            "'": "''",
            '"': '""',
            '\\': '\\\\',
        }
        
        for char, replacement in replacements.items():
            value = value.replace(char, replacement)
        
        return value
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename to prevent path traversal."""
        # Remove path separators
        filename = filename.replace('/', '').replace('\\', '')
        
        # Remove null bytes
        filename = filename.replace('\x00', '')
        
        # Remove suspicious characters
        filename = re.sub(r'[<>:"|?*\x00-\x1f]', '', filename)
        
        # Remove leading dots and spaces
        filename = filename.lstrip('.')
        filename = filename.strip()
        
        # Limit length
        filename = filename[:255]
        
        return filename


class PasswordSecurity:
    """Handle password hashing and verification securely."""
    
    @staticmethod
    def hash_password(password, salt=None):
        """Hash password using SHA-256 (Django handles this internally)."""
        # Note: Django's built-in password hasher (Argon2) should be used
        # This is just for reference
        if not salt:
            import secrets
            salt = secrets.token_hex(32)
        
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        )
        
        return f"{salt}${hash_obj.hex()}"
    
    @staticmethod
    def verify_password(password, hashed):
        """Verify password against hash (Django handles this)."""
        # This is handled by Django's authentication system
        # Use user.check_password(raw_password) instead
        pass


class DataEncryption:
    """Encrypt sensitive data fields."""
    
    @staticmethod
    def generate_cipher_key():
        """Generate a cipher key for encryption."""
        import secrets
        return secrets.token_hex(32)
    
    @staticmethod
    def encrypt_field(value, key):
        """Encrypt a field value using Fernet."""
        if not HAS_CRYPTOGRAPHY:
            logger.warning("cryptography not installed, returning value as-is")
            return value
        
        try:
            from cryptography.fernet import Fernet  # type: ignore
            cipher = Fernet(key)
            encrypted = cipher.encrypt(value.encode('utf-8'))
            return encrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            return None
    
    @staticmethod
    def decrypt_field(encrypted_value, key):
        """Decrypt a field value using Fernet."""
        if not HAS_CRYPTOGRAPHY:
            logger.warning("cryptography not installed, returning value as-is")
            return encrypted_value
        
        try:
            from cryptography.fernet import Fernet, InvalidToken  # type: ignore
            cipher = Fernet(key)
            decrypted = cipher.decrypt(encrypted_value.encode('utf-8'))
            return decrypted.decode('utf-8')
        except InvalidToken:
            logger.error("Decryption failed: Invalid token")
            return None
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            return None


class CORSProtection:
    """Handle CORS (Cross-Origin Resource Sharing) securely."""
    
    ALLOWED_ORIGINS = [
        'http://127.0.0.1:8000',
        'http://localhost:8000',
        'http://etusl:8000',
    ]
    
    @staticmethod
    def validate_origin(origin):
        """Validate if origin is in allowed list."""
        return origin in CORSProtection.ALLOWED_ORIGINS
    
    @staticmethod
    def get_cors_headers(origin):
        """Get CORS headers if origin is valid."""
        if CORSProtection.validate_origin(origin):
            return {
                'Access-Control-Allow-Origin': origin,
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Max-Age': '3600',
            }
        return {}


class CSRFProtection:
    """Additional CSRF protection utilities."""
    
    @staticmethod
    def generate_csrf_token():
        """Generate a CSRF token."""
        import secrets
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def verify_csrf_token(token1, token2):
        """Verify two CSRF tokens match."""
        return hmac.compare_digest(str(token1), str(token2))


class LogSecurity:
    """Security logging utilities."""
    
    @staticmethod
    def log_security_event(event_type, user, details):
        """Log security-related events."""
        logger.warning(
            f"SECURITY_EVENT - Type: {event_type}, User: {user}, Details: {details}"
        )
    
    @staticmethod
    def log_failed_login(username, ip_address):
        """Log failed login attempts."""
        logger.warning(f"FAILED_LOGIN - Username: {username}, IP: {ip_address}")
    
    @staticmethod
    def log_suspicious_activity(activity_type, user, details):
        """Log suspicious user activity."""
        logger.warning(
            f"SUSPICIOUS_ACTIVITY - Type: {activity_type}, User: {user}, Details: {details}"
        )
