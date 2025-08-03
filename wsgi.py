#!/usr/bin/env python3
"""
Production WSGI entry point for deployment platforms.
This file is used by deployment platforms like Heroku, Railway, etc.
"""

import os
import sys

# Import the Flask app
from app import app

# WSGI application object - this is what Gunicorn will use
# Do not include if __name__ == "__main__" block to prevent Flask dev server
