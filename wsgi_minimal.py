#!/usr/bin/env python3
"""
Minimal WSGI test to isolate Railway deployment issues
This bypasses all heavy dependencies to test basic Gunicorn functionality
"""

import os
import sys
import traceback
from datetime import datetime

print("🚀 MINIMAL WSGI DEBUG: Starting...")
print(f"📁 Working directory: {os.getcwd()}")
print(f"🐍 Python version: {sys.version}")
print(f"🌐 PORT env var: {os.environ.get('PORT', 'NOT SET')}")

try:
    # Test Flask import without any heavy dependencies
    from flask import Flask, jsonify
    print("✅ Flask imported successfully")
    
    # Create minimal Flask app
    app = Flask(__name__)
    app.secret_key = 'minimal_test_key'
    
    @app.route('/')
    def hello():
        return jsonify({
            'status': 'SUCCESS',
            'message': 'Minimal WSGI app is working!',
            'timestamp': datetime.now().isoformat(),
            'python_version': sys.version,
            'port': os.environ.get('PORT', 'NOT SET')
        })
    
    @app.route('/health')
    def health():
        return "HEALTHY", 200
    
    # Export for Gunicorn
    application = app
    
    print("✅ MINIMAL WSGI APP: Created successfully")
    print(f"✅ App type: {type(app)}")
    print(f"✅ Application exported: {type(application)}")
    
except Exception as e:
    print(f"❌ MINIMAL WSGI FAILED: {e}")
    traceback.print_exc()
    raise

print("🎯 MINIMAL WSGI: Ready for Gunicorn")