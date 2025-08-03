#!/usr/bin/env python3
"""
Production WSGI entry point for deployment platforms.
This file is used by deployment platforms like Heroku, Railway, etc.
"""

import os
import sys

# Debug: Print environment info for Railway troubleshooting
print("🔍 WSGI Debug Info:")
print(f"   Python version: {sys.version}")
print(f"   PORT env var: {os.environ.get('PORT', 'Not set')}")
print(f"   RAILWAY_ENVIRONMENT: {os.environ.get('RAILWAY_ENVIRONMENT', 'Not set')}")
print(f"   Working directory: {os.getcwd()}")

# Import the Flask app
try:
    from app import app
    print("✅ Successfully imported Flask app")
except Exception as e:
    print(f"❌ Failed to import Flask app: {e}")
    raise

# WSGI application object - this is what Gunicorn will use
# Do not include if __name__ == "__main__" block to prevent Flask dev server
