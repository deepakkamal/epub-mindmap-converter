#!/usr/bin/env python3
"""
MINIMAL WSGI app for debugging Railway 502 issues
This is the simplest possible WSGI app to test Railway deployment
"""

import os
from datetime import datetime

def simple_app(environ, start_response):
    """Minimal WSGI application"""
    status = '200 OK'
    headers = [('Content-type', 'application/json')]
    start_response(status, headers)
    
    response = {
        'status': 'OK',
        'message': 'Minimal WSGI app working!',
        'timestamp': datetime.now().isoformat(),
        'port': os.environ.get('PORT', 'NOT SET'),
        'request_method': environ.get('REQUEST_METHOD'),
        'path_info': environ.get('PATH_INFO'),
        'railway_env': [k for k in os.environ.keys() if 'RAILWAY' in k]
    }
    
    import json
    return [json.dumps(response, indent=2).encode('utf-8')]

# For debugging - test with Gunicorn
if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    port = int(os.environ.get('PORT', 8000))
    print(f"🚀 Testing minimal WSGI app on port {port}")
    
    with make_server('0.0.0.0', port, simple_app) as httpd:
        print(f"✅ Serving on http://0.0.0.0:{port}")
        httpd.serve_forever()

# Export for Gunicorn
app = simple_app