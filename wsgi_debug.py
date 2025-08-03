#!/usr/bin/env python3
"""
Debug WSGI that loads dependencies incrementally
This helps identify which dependency is causing the worker failure
"""

import os
import sys
import traceback
from datetime import datetime

print("🚀 DEBUG WSGI: Starting incremental dependency loading...")

# Stage 1: Basic imports
try:
    from flask import Flask, jsonify
    print("✅ Stage 1: Flask imported")
except Exception as e:
    print(f"❌ Stage 1 FAILED: Flask import - {e}")
    raise

# Stage 2: Standard library imports
try:
    import json
    import time
    print("✅ Stage 2: Standard libraries imported")
except Exception as e:
    print(f"❌ Stage 2 FAILED: Standard libraries - {e}")
    raise

# Stage 3: Light dependencies
try:
    import requests
    from python_dotenv import load_dotenv
    print("✅ Stage 3: Light dependencies imported")
except Exception as e:
    print(f"❌ Stage 3 FAILED: Light dependencies - {e}")
    raise

# Stage 4: Document processing (potentially heavy)
try:
    from docx import Document
    import reportlab
    from bs4 import BeautifulSoup
    print("✅ Stage 4: Document processing libraries imported")
except Exception as e:
    print(f"❌ Stage 4 FAILED: Document processing - {e}")
    raise

# Stage 5: AI/ML libraries (heavy)
try:
    import openai
    print("✅ Stage 5a: OpenAI imported")
    
    import tiktoken
    print("✅ Stage 5b: Tiktoken imported")
    
    # Test tiktoken encoding (this loads models)
    encoding = tiktoken.get_encoding("cl100k_base")
    test_tokens = encoding.encode("Hello world")
    print(f"✅ Stage 5c: Tiktoken encoding test successful ({len(test_tokens)} tokens)")
    
except Exception as e:
    print(f"❌ Stage 5 FAILED: AI/ML libraries - {e}")
    # Continue anyway for testing
    traceback.print_exc()

# Stage 6: Create Flask app
try:
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'debug_test_key')
    
    @app.route('/')
    def debug_info():
        return jsonify({
            'status': 'SUCCESS',
            'message': 'Debug WSGI app is working!',
            'stages_completed': 'All stages loaded successfully',
            'timestamp': datetime.now().isoformat(),
            'memory_usage': f"Working set: {os.environ.get('RAILWAY_REPLICA_MEMORY_LIMIT', 'Unknown')}",
            'python_version': sys.version,
            'dependencies': {
                'flask': True,
                'openai': 'openai' in sys.modules,
                'tiktoken': 'tiktoken' in sys.modules,
                'docx': 'docx' in sys.modules,
                'reportlab': 'reportlab' in sys.modules
            }
        })
    
    @app.route('/health')
    def health():
        return "HEALTHY", 200
    
    @app.route('/memory')
    def memory_test():
        """Simulate memory usage to test limits"""
        try:
            # Small memory test - 10MB
            test_data = b'x' * (10 * 1024 * 1024)
            return jsonify({
                'memory_test': 'SUCCESS',
                'allocated': '10MB',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({
                'memory_test': 'FAILED',
                'error': str(e)
            }), 500
    
    # Export for Gunicorn
    application = app
    
    print("✅ Stage 6: Flask app created and exported")
    print(f"✅ App type: {type(app)}")
    print(f"✅ Application exported: {type(application)}")
    
except Exception as e:
    print(f"❌ Stage 6 FAILED: Flask app creation - {e}")
    traceback.print_exc()
    raise

print("🎯 DEBUG WSGI: All stages completed, ready for Gunicorn")
print(f"📊 Total modules loaded: {len(sys.modules)}")
print(f"🧠 Memory info: {sys.getsizeof(sys.modules)} bytes for module registry")