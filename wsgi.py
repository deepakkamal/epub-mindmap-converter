#!/usr/bin/env python3
"""
Production WSGI entry point for deployment platforms.
This file is used by deployment platforms like Heroku, Railway, etc.
"""

import os
import sys

# Clean Python path - remove duplicates and problematic entries
original_path = sys.path.copy()
cleaned_paths = []
seen = set()

for path in sys.path:
    if path not in seen and 'web_interface' not in path:
        cleaned_paths.append(path)
        seen.add(path)

# Update sys.path and ensure /app is first
sys.path[:] = cleaned_paths
if '/app' in sys.path:
    sys.path.remove('/app')
sys.path.insert(0, '/app')

# Import the Flask application
try:
    from app import app
except Exception as e:
    print(f"CRITICAL: Failed to import Flask app: {e}")
    sys.exit(1)

# Export the Flask app for Gunicorn
application = app

# Note: Do not include if __name__ == "__main__" block to prevent Flask dev server