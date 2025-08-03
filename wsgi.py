#!/usr/bin/env python3
"""
Production WSGI entry point for deployment platforms.
This file is used by deployment platforms like Heroku, Railway, etc.
"""

import os
import sys
import traceback
from datetime import datetime

print(f"🚀 WSGI DEBUG: Starting at {datetime.now()}")
print(f"🐍 Python version: {sys.version}")
print(f"📁 Working directory: {os.getcwd()}")
print(f"🌐 PORT env var: {os.environ.get('PORT', 'NOT SET')}")
print(f"🏗️ All env vars with RAILWAY: {[k for k in os.environ.keys() if 'RAILWAY' in k]}")

# Test if we can import basic modules
try:
    print("🧪 Testing basic imports...")
    import flask
    print(f"✅ Flask version: {flask.__version__}")
    import gunicorn
    print(f"✅ Gunicorn version: {gunicorn.__version__}")
except Exception as e:
    print(f"❌ Basic import failed: {e}")
    traceback.print_exc()

# Import the Flask app with detailed error handling
print("🚀 Attempting to import Flask app...")
try:
    from app import app
    print("✅ Successfully imported 'app' from app.py")
    print(f"📱 App type: {type(app)}")
    print(f"🛠️ App name: {getattr(app, 'name', 'UNKNOWN')}")
    print(f"🔧 App config keys: {list(app.config.keys()) if hasattr(app, 'config') else 'NO CONFIG'}")
except Exception as e:
    print(f"❌ CRITICAL: Failed to import Flask app!")
    print(f"❌ Error: {e}")
    print(f"❌ Error type: {type(e)}")
    traceback.print_exc()
    sys.exit(1)

# Test if app is callable
try:
    print("🧪 Testing if app is WSGI callable...")
    if callable(app):
        print("✅ App is callable (good for WSGI)")
    else:
        print("❌ App is not callable!")
        
    # Test basic app properties
    if hasattr(app, 'wsgi_app'):
        print("✅ App has wsgi_app attribute")
    if hasattr(app, 'run'):
        print("✅ App has run method")
        
except Exception as e:
    print(f"❌ App test failed: {e}")
    traceback.print_exc()

print("🎯 WSGI setup complete - app should be ready for Gunicorn")

# Add network debugging
try:
    import socket
    hostname = socket.gethostname()
    print(f"🌐 Hostname: {hostname}")
    
    # Test if we can bind to the PORT
    port = int(os.environ.get('PORT', 8080))
    print(f"🔌 Attempting to test bind to port {port}...")
    
    # Quick bind test (will release immediately)
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        test_socket.bind(('0.0.0.0', port))
        print(f"✅ Port {port} is available for binding")
        test_socket.close()
    except Exception as bind_error:
        print(f"❌ Cannot bind to port {port}: {bind_error}")
        test_socket.close()
    
except Exception as network_error:
    print(f"❌ Network debugging failed: {network_error}")

# Test app with a dummy WSGI call
try:
    print("🧪 Testing app with dummy WSGI call...")
    
    def start_response(status, headers):
        print(f"📤 WSGI start_response called: {status}")
        
    environ = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/debug/health',
        'QUERY_STRING': '',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': str(os.environ.get('PORT', 8080)),
        'wsgi.version': (1, 0),
        'wsgi.input': None,
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
        'wsgi.url_scheme': 'http'
    }
    
    response = app(environ, start_response)
    print("✅ Dummy WSGI call successful!")
    print(f"📋 Response type: {type(response)}")
    
except Exception as wsgi_test_error:
    print(f"❌ WSGI test failed: {wsgi_test_error}")
    import traceback
    traceback.print_exc()

print("🚀 Final WSGI setup complete!")

# WSGI application object - this is what Gunicorn will use
# Do not include if __name__ == "__main__" block to prevent Flask dev server
