#!/usr/bin/env python3
"""
Dependency check test to ensure all required modules can be imported
This helps catch missing dependencies before deployment
"""

import sys
import traceback

def test_core_dependencies():
    """Test that all core dependencies can be imported"""
    dependencies = [
        'flask',
        'openai', 
        'tiktoken',
        'requests',
        'beautifulsoup4',
        'reportlab',
        'docx',  # python-docx
    ]
    
    failed = []
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError as e:
            print(f"❌ {dep}: {e}")
            failed.append(dep)
    
    return len(failed) == 0

def test_mindmap_core_imports():
    """Test that our custom mindmap_core modules can be imported"""
    try:
        from mindmap_core import MindMapCreator
        from mindmap_core.utils import save_results, clean_filename
        from mindmap_core.extractor import KnowledgeExtractor
        from mindmap_core.mindmap_generator import MindMapGenerator
        print("✅ mindmap_core modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ mindmap_core import failed: {e}")
        traceback.print_exc()
        return False

def test_openai_functionality():
    """Test that OpenAI client can be initialized (without API calls)"""
    try:
        import openai
        # Test client initialization (doesn't make API calls)
        client = openai.OpenAI(api_key="test-key")
        print("✅ OpenAI client can be initialized")
        return True
    except Exception as e:
        print(f"❌ OpenAI client initialization failed: {e}")
        return False

def main():
    """Run all dependency tests"""
    print("🔍 Testing deployment dependencies...\n")
    
    tests = [
        ("Core Dependencies", test_core_dependencies),
        ("MindMap Core Imports", test_mindmap_core_imports), 
        ("OpenAI Functionality", test_openai_functionality),
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        print("-" * 40)
        
        try:
            passed = test_func()
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            traceback.print_exc()
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 All dependency tests passed! Ready for deployment.")
        return 0
    else:
        print("💥 Some tests failed. Check dependencies before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())