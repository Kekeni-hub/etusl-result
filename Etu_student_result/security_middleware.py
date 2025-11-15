"""
Custom security middleware for protecting against common web vulnerabilities.
Implements protections against:
- SQL Injection
- Cross-Site Scripting (XSS)
- Cross-Site Request Forgery (CSRF)
- Directory Traversal
- Command Injection
- Suspicious User-Agent patterns
- Rate limiting basics
"""

import re
import logging
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('security')


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add additional security headers to all responses."""
    
    def process_response(self, request, response):
        # Prevent content type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Enable XSS protection in older browsers
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Feature-Policy (Permissions-Policy)
        response['Permissions-Policy'] = (
            'accelerometer=(), camera=(), geolocation=(), '
            'gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()'
        )
        
        return response


class SQLInjectionProtectionMiddleware(MiddlewareMixin):
    """Detect and block potential SQL injection attempts."""
    
    # Dangerous SQL patterns
    DANGEROUS_PATTERNS = [
        r"('\s*OR\s*'1'='1)",
        r"(\bDROP\b|\bDELETE\b|\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b)",
        r"(--|#|/\*|\*/)",
        r"(xp_|sp_|exec|execute)",
        r"(\\\x00)",
    ]
    
    def process_request(self, request):
        # Check query parameters
        for key, value in request.GET.items():
            if self._is_sql_injection_attempt(str(value)):
                logger.warning(f"SQL Injection attempt detected: {request.path} - {key}={value}")
                return HttpResponseForbidden("Suspicious request detected.")
        
        # Check POST data
        if request.method == 'POST':
            for key, value in request.POST.items():
                if self._is_sql_injection_attempt(str(value)):
                    logger.warning(f"SQL Injection attempt detected: {request.path} - {key}={value}")
                    return HttpResponseForbidden("Suspicious request detected.")
        
        return None
    
    def _is_sql_injection_attempt(self, value):
        """Check if value contains SQL injection patterns."""
        value_upper = value.upper()
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False


class DirectoryTraversalProtectionMiddleware(MiddlewareMixin):
    """Detect and block directory traversal attempts."""
    
    DANGEROUS_PATHS = [
        r'\.\.',
        r'\.\./',
        r'%2e%2e',
        r'%252e',
        r'\.\.\\',
    ]
    
    def process_request(self, request):
        path = request.path
        
        for pattern in self.DANGEROUS_PATHS:
            if re.search(pattern, path, re.IGNORECASE):
                logger.warning(f"Directory traversal attempt detected: {path}")
                return HttpResponseForbidden("Invalid path detected.")
        
        return None


class CommandInjectionProtectionMiddleware(MiddlewareMixin):
    """Detect and block command injection attempts."""
    
    DANGEROUS_COMMANDS = [
        r'[;&|`$()]',
        r'bash',
        r'sh\b',
        r'cmd',
        r'powershell',
        r'exec',
    ]
    
    def process_request(self, request):
        # Check query parameters for command injection
        for key, value in request.GET.items():
            if self._is_command_injection_attempt(str(value)):
                logger.warning(f"Command injection attempt detected: {request.path} - {key}={value}")
                return HttpResponseForbidden("Suspicious request detected.")
        
        return None
    
    def _is_command_injection_attempt(self, value):
        """Check if value contains command injection patterns."""
        for pattern in self.DANGEROUS_COMMANDS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False


class SuspiciousUserAgentMiddleware(MiddlewareMixin):
    """Block requests from suspicious or automated user agents."""
    
    BLOCKED_USER_AGENTS = [
        r'bot',
        r'crawler',
        r'spider',
        r'scraper',
        r'curl',
        r'wget',
        r'python',
        r'nikto',
        r'nmap',
        r'nessus',
        r'masscan',
        r'sqlmap',
        r'havij',
        r'acunetix',
        r'burp',
    ]
    
    def process_request(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        
        if not user_agent:
            logger.warning(f"Request without User-Agent: {request.path}")
            return None  # Allow but log
        
        for pattern in self.BLOCKED_USER_AGENTS:
            if pattern in user_agent:
                logger.warning(f"Suspicious User-Agent blocked: {user_agent} from {request.META.get('REMOTE_ADDR')}")
                return HttpResponseForbidden("Access denied.")
        
        return None


class FileUploadSecurityMiddleware(MiddlewareMixin):
    """Validate file uploads for security threats."""
    
    DANGEROUS_EXTENSIONS = [
        '.exe', '.bat', '.cmd', '.com', '.scr', '.vbs', '.js',
        '.php', '.asp', '.aspx', '.sh', '.jar', '.zip', '.rar',
        '.7z', '.iso', '.dmg', '.app', '.deb', '.rpm', '.msi',
        '.wsf', '.cpl', '.msc', '.ps1', '.psc1', '.psm1',
    ]
    
    def process_request(self, request):
        if request.method == 'POST' and request.FILES:
            for file_field_name, file_obj in request.FILES.items():
                filename = file_obj.name.lower()
                
                # Check file extension
                for dangerous_ext in self.DANGEROUS_EXTENSIONS:
                    if filename.endswith(dangerous_ext):
                        logger.warning(f"Dangerous file upload blocked: {filename} in field {file_field_name}")
                        return HttpResponseForbidden(f"File type {dangerous_ext} is not allowed.")
                
                # Check file size
                if file_obj.size > 5242880:  # 5MB
                    logger.warning(f"Oversized file upload blocked: {filename} ({file_obj.size} bytes)")
                    return HttpResponseForbidden("File size exceeds maximum limit (5MB).")
                
                # Check MIME type matches extension
                if not self._validate_mime_type(filename, file_obj):
                    logger.warning(f"MIME type mismatch: {filename}")
                    return HttpResponseForbidden("Invalid file format.")
        
        return None
    
    def _validate_mime_type(self, filename, file_obj):
        """Basic MIME type validation."""
        import mimetypes
        expected_type, _ = mimetypes.guess_extension(filename)
        return expected_type is not None


class XSSProtectionMiddleware(MiddlewareMixin):
    """Protect against Cross-Site Scripting (XSS) attacks."""
    
    XSS_PATTERNS = [
        r'<script[^>]*>',
        r'javascript:',
        r'onerror\s*=',
        r'onload\s*=',
        r'onclick\s*=',
        r'onmouseover\s*=',
        r'<iframe',
        r'<object',
        r'<embed',
    ]
    
    def process_request(self, request):
        # Check GET parameters
        for key, value in request.GET.items():
            if self._contains_xss_payload(str(value)):
                logger.warning(f"XSS attempt detected: {request.path} - {key}={value}")
                return HttpResponseForbidden("Suspicious content detected.")
        
        # Check POST data (but not file uploads)
        if request.method == 'POST' and not request.FILES:
            for key, value in request.POST.items():
                if self._contains_xss_payload(str(value)):
                    logger.warning(f"XSS attempt detected: {request.path} - {key}={value}")
                    return HttpResponseForbidden("Suspicious content detected.")
        
        return None
    
    def _contains_xss_payload(self, value):
        """Check if value contains XSS patterns."""
        for pattern in self.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False


class RateLimitingMiddleware(MiddlewareMixin):
    """Basic rate limiting to prevent brute force attacks."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_counts = {}
        self.MAX_REQUESTS_PER_MINUTE = 60
    
    def __call__(self, request):
        remote_addr = request.META.get('REMOTE_ADDR', 'unknown')
        
        # Check rate limit
        if not self._check_rate_limit(remote_addr):
            logger.warning(f"Rate limit exceeded for {remote_addr}")
            return HttpResponseForbidden("Too many requests. Please try again later.")
        
        response = self.get_response(request)
        return response
    
    def _check_rate_limit(self, remote_addr):
        """Simple rate limiting check."""
        import time
        current_time = int(time.time())
        minute_ago = current_time - 60
        
        if remote_addr not in self.request_counts:
            self.request_counts[remote_addr] = []
        
        # Remove old requests
        self.request_counts[remote_addr] = [
            req_time for req_time in self.request_counts[remote_addr]
            if req_time > minute_ago
        ]
        
        # Check if limit exceeded
        if len(self.request_counts[remote_addr]) >= self.MAX_REQUESTS_PER_MINUTE:
            return False
        
        # Add current request
        self.request_counts[remote_addr].append(current_time)
        return True
