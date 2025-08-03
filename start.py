#!/usr/bin/env python3
"""
Production startup script that forces the use of Gunicorn.
This prevents Railway from accidentally running the Flask development server.
"""

import os
import sys
import subprocess

def main():
    """Main startup function for production deployment."""
    
    # Check if we're in a production environment
    production_indicators = [
        'RAILWAY_ENVIRONMENT',
        'HEROKU_APP_NAME', 
        'PORT'  # Railway and most deployment platforms set PORT
    ]
    
    is_production = any(os.environ.get(indicator) for indicator in production_indicators)
    
    if is_production:
        print("🚀 Production environment detected!")
        print("🔧 Starting with Gunicorn production server...")
        
        # Get the port from environment
        port = os.environ.get('PORT', '8080')
        
        # Construct the Gunicorn command
        gunicorn_cmd = [
            'gunicorn',
            '--bind', f'0.0.0.0:{port}',
            'wsgi:app',
            '--workers', '2',
            '--timeout', '120',
            '--preload',
            '--access-logfile', '-',
            '--error-logfile', '-'
        ]
        
        print(f"📋 Command: {' '.join(gunicorn_cmd)}")
        
        # Execute Gunicorn
        try:
            subprocess.exec(gunicorn_cmd)
        except Exception as e:
            print(f"❌ Failed to start Gunicorn: {e}")
            sys.exit(1)
    else:
        print("💻 Local development detected - use 'python app.py' for development server")
        sys.exit(1)

if __name__ == "__main__":
    main()