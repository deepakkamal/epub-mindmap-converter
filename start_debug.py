#!/usr/bin/env python3
"""
Debug wrapper for Gunicorn startup to catch any startup failures
"""

import os
import sys
import subprocess
import time
from datetime import datetime

print(f"🚀 DEBUG STARTUP WRAPPER: {datetime.now()}")
print(f"🐍 Python: {sys.executable}")
print(f"📁 Working dir: {os.getcwd()}")
print(f"🌐 PORT: {os.environ.get('PORT', 'NOT SET')}")

# Fix Python path issues first
print(f"🔧 Fixing Python path issues...")
original_path = sys.path.copy()
print(f"   Original: {original_path}")

# Remove duplicates and problematic paths
cleaned_paths = []
seen = set()
for path in sys.path:
    if path not in seen and 'web_interface' not in path:
        cleaned_paths.append(path)
        seen.add(path)

sys.path[:] = cleaned_paths
if '/app' in sys.path:
    sys.path.remove('/app')
sys.path.insert(0, '/app')
print(f"✅ Fixed Python path: {sys.path[:3]}...")

# Test WSGI import one more time
print("🧪 Testing WSGI import in startup wrapper...")
try:
    import wsgi
    print("✅ wsgi.py imports successfully")
    print(f"📱 App object: {wsgi.app}")
except Exception as e:
    print(f"❌ WSGI import failed in wrapper: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Build Gunicorn command
port = os.environ.get('PORT', '8080')
cmd = [
    'gunicorn',
    'wsgi:app',
    '--bind', f'0.0.0.0:{port}',
    '--workers', '1',
    '--timeout', '120',
    '--log-level', 'info',
    '--access-logfile', '-',
    '--error-logfile', '-'
]

print(f"🚀 Starting Gunicorn with command:")
print(f"   {' '.join(cmd)}")

try:
    # Start Gunicorn
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    # Monitor the first few seconds of output
    print("📊 Monitoring Gunicorn startup...")
    start_time = time.time()
    
    while True:
        output = process.stdout.readline()
        if output:
            print(f"GUNICORN: {output.strip()}")
        
        if process.poll() is not None:
            print(f"❌ Gunicorn process exited with code: {process.returncode}")
            break
            
        # After 10 seconds, if still running, switch to normal mode
        if time.time() - start_time > 10:
            print("✅ Gunicorn appears to be starting successfully, switching to normal mode...")
            # Wait for the process to finish
            process.wait()
            break
            
        time.sleep(0.1)
        
except Exception as e:
    print(f"❌ Failed to start Gunicorn: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)