# Mind Map Framework Testing Guide

## 🧪 Comprehensive Unit Testing Suite

This testing suite ensures all components of the Mind Map Framework work correctly for deployment verification.

## 📁 Test Structure

```
tests/
├── __init__.py                 # Package initialization
├── test_docx_creator.py        # DOCX generation tests
├── test_mindmap_core.py        # Core mind map functionality tests
├── test_epub_processor.py      # EPUB processing tests
├── test_app_functions.py       # Flask app function tests
├── test_utils.py              # Utility function tests
├── run_all_tests.py           # Comprehensive test runner
├── run_tests.bat              # Windows batch script
├── simple_test_runner.py      # Quick deployment verification
├── requirements.txt           # Testing dependencies
├── test_data/                 # Sample test data
│   ├── sample_content.txt
│   └── sample_epub_content.txt
└── TESTING_GUIDE.md           # This file
```

## 🚀 Quick Deployment Verification

For quick deployment verification, use the dedicated deployment test script:

```bash
# Option 1: Python script (cross-platform)
conda activate mind_map
cd web_interface/tests
python deployment_test.py

# Option 2: Windows batch file (Windows only)
cd web_interface/tests
quick_test.bat
```

**Expected output:**
```
🧪 Mind Map Framework - Quick Deployment Test
==================================================

🔍 Testing Dependencies...
  ✅ All dependencies available

🔧 Testing Core Modules...
  ✅ DOCX creator module
  ✅ Title formatting: Chapter 2: How To Almost Make Anything
  ✅ DOCX creation: BytesIO object

📊 Test Results
==============================
✅ All tests passed!
🚀 Framework is ready for deployment!
```

## 🔧 Full Test Suite

### Prerequisites

Ensure you're in the conda environment:
```bash
conda activate mind_map
cd web_interface/tests
```

### Install Testing Dependencies

```bash
# Core testing framework
conda install pytest pytest-mock -y

# Additional dependencies (if needed)
pip install python-docx beautifulsoup4
```

### Running Tests

#### Option 1: Quick Test (Recommended for deployment)
```bash
python run_all_tests.py --check-deps
```

#### Option 2: Run Specific Module Tests
```bash
python run_all_tests.py --module docx_creator
python run_all_tests.py --module mindmap_core
```

#### Option 3: Full Test Suite (Advanced)
```bash
python run_all_tests.py --verbose
```

#### Option 4: Windows Batch Script
```bash
run_tests.bat
```

## 📊 Test Coverage

### Core Functionality Tests
- ✅ **Title Formatting**: Chapter name conversion and cleaning
- ✅ **Markdown Cleaning**: Removal of markdown remnants
- ✅ **DOCX Creation**: Single and multi-chapter document generation
- ✅ **Legacy Compatibility**: Backward compatibility with existing functions

### Integration Tests
- ✅ **Dependencies**: All required packages available
- ✅ **Module Imports**: Core modules can be imported
- ✅ **End-to-End**: Complete workflow functionality

### Framework Components
- 🧪 **Mind Map Core**: AI-powered analysis and generation
- 🧪 **EPUB Processor**: File extraction and content processing
- 🧪 **Flask App**: Web interface and API endpoints
- 🧪 **Utilities**: Helper functions and file operations

## 🎯 Expected Test Results

### Successful Test Run
```
🧪 Mind Map Framework Test Suite
==================================================
Started at: 2025-01-XX XX:XX:XX

🔍 Checking Dependencies...
  ✅ pytest
  ✅ python-docx
  ✅ requests
  ✅ flask

✅ All required dependencies available

📊 Test Summary
==================================================
Duration: 0:00:XX
Finished at: 2025-01-XX XX:XX:XX
✅ All tests passed!

🚀 System is ready for deployment
```

### If Tests Fail
- Check that you're in the correct conda environment
- Verify all dependencies are installed
- Review error messages for specific issues
- Fix failing components before deployment

## 🔍 Test Details

### test_docx_creator.py
- **TestTitleFormatting**: Validates chapter title conversion
- **TestMarkdownCleaning**: Ensures markdown syntax removal
- **TestDOCXCreation**: Verifies document generation
- **TestInlineFormatting**: Tests text formatting preservation

### test_mindmap_core.py
- **TestKnowledgeExtractor**: AI analysis pipeline
- **TestMindMapGenerator**: Mermaid diagram creation
- **TestNotesGenerator**: Summary and explanation generation
- **TestContentSynthesizer**: Content combination

### test_epub_processor.py
- **TestEpubChapterExtractor**: File extraction and processing
- **Content classification and cleaning**
- **Chapter ordering and validation**

### test_app_functions.py
- **TestProcessingManager**: Session and progress tracking
- **TestDocxFromMemoryData**: In-memory document creation
- **Error handling and validation**

### test_utils.py
- **TestFilenameUtils**: File naming and cleaning
- **TestFileOperations**: File saving and management
- **TestValidation**: Result validation and reporting

## 💡 Tips for Deployment

1. **Always run tests** before deploying a new version
2. **Use the conda environment** for consistency
3. **Check dependencies** first if tests fail
4. **Run quick tests** for rapid deployment verification
5. **Full test suite** for major updates or releases

## 🚨 Common Issues

### ImportError: No module named 'xxx'
```bash
# Solution: Install missing dependency
pip install missing-package
```

### Tests fail in wrong directory
```bash
# Solution: Navigate to correct directory
cd web_interface/tests
```

### Permission errors
```bash
# Solution: Run as administrator (Windows) or check file permissions
```

---

**Ready for Production**: When all tests pass, your Mind Map Framework is ready for deployment! 🚀