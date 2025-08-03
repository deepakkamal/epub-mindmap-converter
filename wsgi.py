#!/usr/bin/env python3
"""
Production WSGI entry point for deployment platforms.
This file is used by deployment platforms like Heroku, Railway, etc.
"""

import os
from app import app

# For Gunicorn deployment
if __name__ == "__main__":
    # Fallback for direct execution (development only)
    port = int(os.environ.get('PORT', 5000))
    print("WARNING: Running with Flask development server. Use Gunicorn for production.")
    app.run(host='0.0.0.0', port=port)
