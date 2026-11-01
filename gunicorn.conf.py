"""
StudySignal - Gunicorn Production Configuration
Configures production WSGI server for Render deployment.
"""

import os

# Dynamic port binding provided by Render ($PORT)
port = os.environ.get("PORT", "10000")
bind = f"0.0.0.0:{port}"

# Worker processes & concurrency for production free tier
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
threads = int(os.environ.get("PYTHON_THREADS", "2"))
timeout = int(os.environ.get("WEB_TIMEOUT", "120"))

# Standard I/O logging for Render log streaming
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("LOG_LEVEL", "info")
