# Production configuration for Flask
import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'replace-this-with-a-strong-random-value')

# Session configuration - adapt to proxy environment
# Set to True only if the proxy provides HTTPS
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# File upload limit
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB upload limit

# Proxy configuration
# Set to True if running behind a reverse proxy
PREFERRED_URL_SCHEME = os.environ.get('PREFERRED_URL_SCHEME', 'http')

# Trust proxy headers (important for reverse proxy)
# Set to True if your reverse proxy is trusted
PROXY_FIX = os.environ.get('PROXY_FIX', 'False').lower() == 'true'
