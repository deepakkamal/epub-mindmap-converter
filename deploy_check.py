#!/usr/bin/env python3
"""
Pre-deployment verification script for Mind Map Interface
Run this before deploying to ensure everything is ready.
"""

import os
import sys
import importlib

def check_dependencies():
    """Check if all required dependencies are available"""
    required_deps = [
        ('flask', 'Flask'),
        ('requests', 'requests'),
        ('docx', 'python-docx'),
        ('reportlab', 'reportlab'),
        ('bs4', 'beautifulsoup4')
    ]
    
    print("🔍 Checking dependencies...")
    missing = []
    
    for import_name, package_name in required_deps:
        try:
            importlib.import_module(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            missing.append(package_name)
            print(f"❌ {package_name} - MISSING")
    
    return missing

def check_files():
    """Check if all required deployment files exist"""
    required_files = [
        'app.py',
        'wsgi.py',
        'requirements.txt',
        'Procfile',
        'vercel.json',
        'Dockerfile',
        'simple_pdf_creator.py',
        'simple_docx_creator.py'
    ]
    
    print("\n📁 Checking deployment files...")
    missing = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            missing.append(file)
            print(f"❌ {file} - MISSING")
    
    return missing

def check_functionality():
    """Basic functionality test"""
    print("\n🧪 Testing core functionality...")
    
    try:
        # Test PDF creator
        from simple_pdf_creator import create_pdf
        sample_data = {
            'mindmaps': {'comprehensive_mindmap': '''mindmap
  root((Test Deployment))
    feature1[PDF Generation]
    feature2[DOCX Creation]
    feature3[Mind Map Analysis]'''},
            'mindmap_explanation': 'Test explanation of deployment verification.',
            'quick_summary': 'Test summary for deployment check.',
            'analysis_summary': 'Test analysis to verify functionality.'
        }
        result = create_pdf(('test', sample_data))
        print(f"✅ PDF generation working ({len(result.getvalue())} bytes)")
        
        # Test DOCX creator  
        from simple_docx_creator import create_docx
        result = create_docx(('test', sample_data))
        print(f"✅ DOCX generation working ({len(result.getvalue())} bytes)")
        
        # Test Flask app imports
        import app
        print("✅ Flask app imports successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def main():
    """Main deployment readiness check"""
    print("🚀 Mind Map Interface - Deployment Readiness Check")
    print("=" * 55)
    
    # Check dependencies
    missing_deps = check_dependencies()
    
    # Check files
    missing_files = check_files()
    
    # Test functionality
    functionality_ok = check_functionality()
    
    # Summary
    print("\n" + "=" * 55)
    print("📋 DEPLOYMENT READINESS SUMMARY")
    print("=" * 55)
    
    if missing_deps:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        print("   Run: pip install -r requirements.txt")
    else:
        print("✅ All dependencies available")
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
    else:
        print("✅ All deployment files present")
    
    if functionality_ok:
        print("✅ Core functionality working")
    else:
        print("❌ Functionality issues detected")
    
    # Final verdict
    if not missing_deps and not missing_files and functionality_ok:
        print("\n🎉 READY FOR DEPLOYMENT!")
        print("\nNext steps:")
        print("1. Push code to GitHub")
        print("2. Choose deployment platform (Railway recommended)")
        print("3. Set OPENAI_API_KEY environment variable")
        print("4. Deploy!")
    else:
        print("\n⚠️  DEPLOYMENT ISSUES DETECTED")
        print("Please fix the issues above before deploying.")
    
    return len(missing_deps) == 0 and len(missing_files) == 0 and functionality_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)