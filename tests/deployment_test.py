#!/usr/bin/env python3
"""
Quick Deployment Test for Mind Map Framework

Run this script to verify the system is ready for deployment.
"""

import sys
import os

def main():
    """Run deployment verification tests"""
    print('🧪 Mind Map Framework - Quick Deployment Test')
    print('=' * 50)
    
    # Test 1: Dependencies
    print('\n🔍 Testing Dependencies...')
    try:
        import pytest
        import docx
        import requests
        import flask
        print('  ✅ All dependencies available')
        dependencies_ok = True
    except ImportError as e:
        print(f'  ❌ Missing dependency: {e}')
        dependencies_ok = False
    
    # Test 2: Core modules
    print('\n🔧 Testing Core Modules...')
    sys.path.insert(0, '..')
    
    try:
        from simple_docx_creator import create_docx, _format_chapter_title
        print('  ✅ DOCX creator module')
        
        # Test title formatting
        title = _format_chapter_title('07_chapter_chapter-2-how-to-almost-make-anything')
        print(f'  ✅ Title formatting: {title}')
        
        # Test basic DOCX creation
        sample_data = {
            'mindmaps': {'comprehensive_mindmap': 'mindmap\n  root((Test))'},
            'quick_summary': 'Test summary'
        }
        result = create_docx(('test', sample_data))
        print(f'  ✅ DOCX creation: {type(result).__name__} object')
        
        modules_ok = True
        
    except Exception as e:
        print(f'  ❌ Module test failed: {e}')
        modules_ok = False
    
    # Summary
    print('\n📊 Test Results')
    print('=' * 30)
    
    if dependencies_ok and modules_ok:
        print('✅ All tests passed!')
        print('🚀 Framework is ready for deployment!')
        return 0
    else:
        print('❌ Some tests failed!')
        print('🔧 Please fix issues before deployment')
        return 1

if __name__ == '__main__':
    sys.exit(main())