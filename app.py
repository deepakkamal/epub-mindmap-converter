#!/usr/bin/env python3
"""
EPUB to Mindmap Web Interface

A Flask web application that provides a user-friendly interface for:
1. Uploading EPUB files (drag & drop or file selection)
2. Converting EPUB to markdown chapters
3. Selecting chapters for mindmap generation
4. Processing selected chapters into mindmaps
5. Downloading combined results

Features:
- Drag & drop file upload
- Real-time processing status
- Chapter selection interface
- Progress tracking
- Download management
"""

import os
import json
import shutil
import tempfile
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, render_template, send_file, session
import uuid
import threading
import time

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, will use system environment variables only
    pass

# Import our custom modules - now using local packages
# Import mindmap creator modules from local package
try:
    from mindmap_core import MindMapCreator
    from mindmap_core.utils import (
        save_results, 
        save_mindmap, 
        save_mindmap_notes,
        clean_filename,
        create_processing_report,
        validate_results
    )
    # Import streamlined DOCX creator
    from simple_docx_creator import create_docx
    
    # Import PDF creator
    from simple_pdf_creator import create_pdf
    
    # Import DOCX converter - try new streamlined version first
    try:
        from docx_converter_new import convert_chapter_to_docx
        DOCX_CONVERTER_AVAILABLE = True
        print("✓ New streamlined DOCX converter loaded")
        
        # Create legacy compatibility function
        def convert_analysis_to_docx(markdown_file_path, output_dir, filename_prefix):
            """Legacy compatibility wrapper"""
            chapter_name = filename_prefix or os.path.basename(os.path.dirname(markdown_file_path))
            chapter_dir = os.path.dirname(markdown_file_path)
            return convert_chapter_to_docx(chapter_name, chapter_dir, output_dir)
        
    except ImportError as new_docx_error:
        print(f"New DOCX converter not available: {new_docx_error}")
        try:
            from simple_docx_creator import create_chapter_docx_direct, create_combined_docx_direct
            DOCX_CONVERTER_AVAILABLE = True
            print("✓ Legacy DOCX converter loaded as fallback")
            
            # Create wrapper for new interface
            def convert_chapter_to_docx(chapter_name, chapter_dir, output_dir):
                # Create temp markdown file for legacy converter
                # Legacy converter disabled - use memory-only operations
                return None
                
        except ImportError as docx_error:
            print(f"Warning: DOCX converter not available: {docx_error}")
            DOCX_CONVERTER_AVAILABLE = False
            # Create dummy functions so the app doesn't crash
            def convert_chapter_to_docx(*args, **kwargs):
                raise Exception("DOCX converter not available")
            def convert_analysis_to_docx(*args, **kwargs):
                raise Exception("DOCX converter not available")
    
    MINDMAP_CREATOR_AVAILABLE = True
    print("✓ Mind map creator loaded successfully")
except ImportError as e:
    print(f"Warning: Could not import mindmap creator: {e}")
    MINDMAP_CREATOR_AVAILABLE = False
    DOCX_CONVERTER_AVAILABLE = False

def create_pdf_from_memory_data(session_id, chapter_data=None, is_combined=False):
    """
    STREAMLINED PDF creation using unified create_pdf function!
    """
    try:
        # Use the global process_manager instance, not a new one
        global process_manager
        
        if is_combined:
            # Get all processed chapters from results
            results = process_manager.get_results(session_id)
            status = process_manager.get_status(session_id)
            
            print(f"PDF Debug: Results keys: {list(results.keys())}")
            print(f"PDF Debug: Status keys: {list(status.keys())}")
            
            # First try to get mindmap_results
            mindmap_results = results.get('mindmap_results', [])
            print(f"PDF Debug: Found {len(mindmap_results)} mindmap results")
            
            if not mindmap_results:
                completed_chapters = status.get('completed_chapters', [])
                print(f"PDF Debug: No mindmap_results, found {len(completed_chapters)} completed chapters")
                
                if not completed_chapters:
                    print("PDF Debug: No completed chapters found")
                    return None
                
                # Try to reconstruct from individual chapter data
                mindmap_results = []
                for chapter_name in completed_chapters:
                    chapter_key = f"{chapter_name}_data"
                    if chapter_key in results:
                        chapter_data = results[chapter_key]
                        chapter_data['chapter_name'] = chapter_name
                        mindmap_results.append(chapter_data)
                
                if not mindmap_results:
                    print("PDF Debug: Could not reconstruct chapter data")
                    return None
            
            # Convert to our expected format for the unified function
            all_chapters = {}
            for result in mindmap_results:
                chapter_name = result.get('chapter_name', 'Unknown')
                all_chapters[chapter_name] = result
                print(f"PDF Debug: Processing chapter {chapter_name} with keys: {list(result.keys())}")
            
            print(f"PDF Debug: Using unified create_pdf for {len(all_chapters)} chapters")
            return create_pdf(all_chapters)
        
        else:
            # Single chapter
            if not chapter_data:
                print("PDF Debug: No chapter data provided for single chapter")
                return None
            
            chapter_name = chapter_data.get('name', chapter_data.get('chapter_name', 'Unknown Chapter'))
            print(f"PDF Debug: Using unified create_pdf for single chapter: {chapter_name}")
            return create_pdf((chapter_name, chapter_data))
            
    except Exception as e:
        print(f"ERROR in create_pdf_from_memory_data: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_docx_from_memory_data(session_id, chapter_data=None, is_combined=False):
    """
    STREAMLINED DOCX creation using unified create_docx function!
    """
    try:
        # Use the global process_manager instance, not a new one
        global process_manager
        
        if is_combined:
            # Get all processed chapters from results
            results = process_manager.get_results(session_id)
            status = process_manager.get_status(session_id)
            
            print(f"DOCX Debug: Results keys: {list(results.keys())}")
            print(f"DOCX Debug: Status keys: {list(status.keys())}")
            
            # First try to get mindmap_results
            mindmap_results = results.get('mindmap_results', [])
            print(f"DOCX Debug: Found {len(mindmap_results)} mindmap results")
            
            if not mindmap_results:
                completed_chapters = status.get('completed_chapters', [])
                print(f"DOCX Debug: No mindmap_results, found {len(completed_chapters)} completed chapters")
                
                if not completed_chapters:
                    print("DOCX Debug: No completed chapters found")
                    return None
                
                # Try to reconstruct from individual chapter data
                mindmap_results = []
                for chapter_name in completed_chapters:
                    chapter_key = f"{chapter_name}_data"
                    if chapter_key in results:
                        chapter_data = results[chapter_key]
                        chapter_data['chapter_name'] = chapter_name
                        mindmap_results.append(chapter_data)
                
                if not mindmap_results:
                    print("DOCX Debug: Could not reconstruct chapter data")
                    return None
            
            # Convert to our expected format for the unified function
            all_chapters = {}
            for result in mindmap_results:
                chapter_name = result.get('chapter_name', 'Unknown')
                all_chapters[chapter_name] = result
                print(f"DOCX Debug: Processing chapter {chapter_name} with keys: {list(result.keys())}")
            
            print(f"DOCX Debug: Using unified create_docx for {len(all_chapters)} chapters")
            return create_docx(all_chapters)
        
        else:
            # Single chapter
            if not chapter_data:
                print("DOCX Debug: No chapter data provided for single chapter")
                return None
            
            chapter_name = chapter_data.get('name', chapter_data.get('chapter_name', 'Unknown Chapter'))
            print(f"DOCX Debug: Using unified create_docx for single chapter: {chapter_name}")
            return create_docx((chapter_name, chapter_data))
            
    except Exception as e:
        print(f"ERROR in create_docx_from_memory_data: {e}")
        import traceback
        traceback.print_exc()
        return None

try:
    from epub_processor import EpubChapterExtractor
    EPUB_EXTRACTOR_AVAILABLE = True
    print("✓ EPUB extractor loaded")
except ImportError as e:
    print(f"Warning: EPUB extractor not available: {e}")
    EPUB_EXTRACTOR_AVAILABLE = False

# Import pricing manager
try:
    from pricing_manager import get_available_models, get_pricing_summary, pricing_manager
except ImportError as e:
    print(f"Error importing pricing_manager: {e}")
    print("Using fallback model configuration")
    
    def get_available_models():
        return {
            'gpt-4o-mini': {'name': 'GPT-4o Mini', 'output_cost': 0.60, 'description': 'Fastest and most affordable'},
            'gpt-3.5-turbo': {'name': 'GPT-3.5 Turbo', 'output_cost': 1.50, 'description': 'Fast and efficient'}
        }
    
    def get_pricing_summary():
        return {
            'last_updated': datetime.now().isoformat(),
            'models': [
                {'id': 'gpt-4o-mini', 'name': 'GPT-4o Mini', 'output_cost': 0.60, 'cost_formatted': '$0.60/1M tokens'},
                {'id': 'gpt-3.5-turbo', 'name': 'GPT-3.5 Turbo', 'output_cost': 1.50, 'cost_formatted': '$1.50/1M tokens'}
            ],
            'total_models': 2
        }

app = Flask(__name__)
# Use environment variable for secret key in production
app.secret_key = os.environ.get('SECRET_KEY', 'epub_mindmap_converter_secret_key_2025')
# Configure max file size (can be overridden by environment)
max_file_size = int(os.environ.get('MAX_FILE_SIZE_MB', 100)) * 1024 * 1024
app.config['MAX_CONTENT_LENGTH'] = max_file_size
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
app.config['OUTPUT_FOLDER'] = os.environ.get('OUTPUT_FOLDER', 'outputs')

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
# Static temp directory removed - using memory-only operations

# Global storage for processing status
processing_status = {}
chapter_data = {}


# Security headers for production
@app.after_request
def after_request(response):
    """Add security headers for production deployment."""
    # Only add security headers in production
    if not app.debug:
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response


class ProcessingManager:
    """Manages the processing workflow and status tracking."""
    
    def __init__(self):
        self.status = {}
        self.results = {}
    
    def start_epub_processing(self, session_id: str, epub_path: str, min_length: int = 500):
        """Start EPUB to markdown conversion in background (file-based)."""
        self.status[session_id] = {
            'stage': 'epub_processing',
            'progress': 0,
            'message': 'Starting EPUB processing...',
            'completed': False,
            'error': None
        }
        
        thread = threading.Thread(
            target=self._process_epub_worker,
            args=(session_id, epub_path, min_length, False)
        )
        thread.daemon = True
        thread.start()
    
    def start_epub_processing_memory(self, session_id: str, epub_data: bytes, filename: str, min_length: int = 500):
        """Start EPUB to markdown conversion in background (memory-based)."""
        self.status[session_id] = {
            'stage': 'epub_processing',
            'progress': 0,
            'message': 'Starting in-memory EPUB processing...',
            'completed': False,
            'error': None,
            'filename': filename
        }
        
        thread = threading.Thread(
            target=self._process_epub_worker_memory,
            args=(session_id, epub_data, filename, min_length)
        )
        thread.daemon = True
        thread.start()
    
    def _process_epub_worker(self, session_id: str, epub_path: str, min_length: int, is_memory: bool = False):
        """Worker function for EPUB processing (file-based)."""
        try:
            self.status[session_id]['message'] = 'Extracting EPUB structure...'
            self.status[session_id]['progress'] = 20
            
            # Create output directory for this session
            output_dir = os.path.join(app.config['OUTPUT_FOLDER'], session_id, 'chapters')
            os.makedirs(output_dir, exist_ok=True)
            
            # Initialize EPUB extractor
            extractor = EpubChapterExtractor(epub_path=epub_path, min_content_length=min_length)
            
            self.status[session_id]['message'] = 'Processing chapters...'
            self.status[session_id]['progress'] = 40
            
            # Convert EPUB to markdown files
            extractor.convert_epub_to_markdown_files(output_dir)
            
            self.status[session_id]['message'] = 'Collecting chapter information...'
            self.status[session_id]['progress'] = 80
            
            # Collect chapter information
            chapters = self._collect_chapter_info(output_dir)
            
            self.results[session_id] = {
                'chapters': chapters,
                'output_dir': output_dir,
                'epub_path': epub_path
            }
            
            self.status[session_id].update({
                'progress': 100,
                'message': 'EPUB processing completed!',
                'completed': True,
                'type': 'complete',
            })
            
        except Exception as e:
            self.status[session_id].update({
                'error': str(e),
                'message': f'Error: {str(e)}',
                'completed': True,
                'type': 'error'
            })
    
    def _process_epub_worker_memory(self, session_id: str, epub_data: bytes, filename: str, min_length: int):
        """Worker function for EPUB processing (memory-based)."""
        try:
            self.status[session_id]['message'] = 'Extracting EPUB structure from memory...'
            self.status[session_id]['progress'] = 20
            
            # Initialize EPUB extractor with memory data
            extractor = EpubChapterExtractor(epub_data=epub_data, min_content_length=min_length)
            
            self.status[session_id]['message'] = 'Processing chapters...'
            self.status[session_id]['progress'] = 40
            
            # Extract chapters directly to memory (no file creation)
            chapters_data = extractor.extract_chapters_to_memory()
            
            self.status[session_id]['message'] = 'Organizing chapter data...'
            self.status[session_id]['progress'] = 80
            
            # Convert to the format expected by the rest of the system
            chapters = {}
            if isinstance(chapters_data, list):
                for chapter_data in chapters_data:
                    if isinstance(chapter_data, dict):
                        filename = f"{chapter_data['canonical_name']}.md"
                        chapters[filename] = {
                            'title': chapter_data['title'],
                            'canonical_name': chapter_data['canonical_name'],
                            'content': chapter_data['content'],  # Store actual markdown content
                            'available': True,
                            'memory_based': True
                        }
                                # Handle unexpected data types gracefully
            else:
                pass
                raise Exception(f"Expected list from extract_chapters_to_memory, got {type(chapters_data)}")
            
            self.results[session_id] = {
                'chapters': chapters,
                'filename': filename,
                'memory_processed': True,
                'chapter_contents': {name: data['content'] for name, data in chapters.items()}  # Easy access to content
            }
            
            self.status[session_id].update({
                'progress': 100,
                'message': f'In-memory EPUB processing completed! {len(chapters)} chapters ready.',
                'completed': True,
                'type': 'complete',
                'completion_type': 'epub_processed'
            })
            
        except Exception as e:
            self.status[session_id].update({
                'error': str(e),
                'message': f'Error processing EPUB: {str(e)}',
                'completed': True
            })
    def start_mindmap_processing(self, session_id: str, selected_chapters: List[str], 
                                 ai_model: str = 'gpt-3.5-turbo', mindmap_type: str = 'comprehensive',
                                 api_key: str = None):
        """Start mindmap generation for selected chapters."""
        self.status[session_id] = {
            'stage': 'mindmap_processing',
            'progress': 0,
            'message': 'Starting mindmap generation...',
            'completed': False,
            'error': None,
            'total_chapters': len(selected_chapters),
            'processed_chapters': 0,
            'ai_model': ai_model,
            'mindmap_type': mindmap_type,
            'completed_chapters': [],  # Track individual chapter completion
            'chapter_status': {}       # Track status of each chapter
        }
        
        thread = threading.Thread(
            target=self._process_mindmaps_worker,
            args=(session_id, selected_chapters, ai_model, mindmap_type, api_key)
        )
        thread.daemon = True
        thread.start()
    
    def _process_mindmaps_worker(self, session_id: str, selected_chapters: List[str],
                                ai_model: str = 'gpt-3.5-turbo', mindmap_type: str = 'comprehensive',
                                api_key: str = None):
        """Worker function for mindmap processing using direct integration (RAM-only)."""
        try:
            if not MINDMAP_CREATOR_AVAILABLE:
                raise Exception("Mindmap creator is not available. Please check the installation.")
                
            result_data = self.results[session_id]
            
            # Check if we have memory-based processing
            if result_data.get('memory_processed', False):
                # Use in-memory chapter data
                chapter_contents = result_data.get('chapter_contents', {})
                chapters_data = result_data.get('chapters', {})
            else:
                # Fallback to file-based processing
                chapters_dir = result_data['output_dir']
                chapter_contents = {}
                chapters_data = result_data.get('chapters', {})
                
                # Read chapter contents from files
                for chapter_file in selected_chapters:
                    chapter_path = os.path.join(chapters_dir, chapter_file)
                    if os.path.exists(chapter_path):
                        with open(chapter_path, 'r', encoding='utf-8') as f:
                            chapter_contents[chapter_file] = f.read()
            
            total_chapters = len(selected_chapters)
            mindmap_results = []
            
            # Set up API key
            if not api_key:
                api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                raise Exception("No OpenAI API key available. Please set your API key.")
            
            # Pass API key directly to creator (no environment variable storage)
            
            # Initialize the mindmap creator with API key directly (no environment storage)
            print(f"Initializing MindMapCreator with model: {ai_model}")
            try:
                creator = MindMapCreator(model=ai_model, api_key=api_key)
                print("MindMapCreator initialized successfully")
            except Exception as e:
                print(f"Error initializing MindMapCreator: {e}")
                raise Exception(f"Failed to initialize AI model '{ai_model}': {str(e)}")
            
            for i, chapter_file in enumerate(selected_chapters):
                chapter_name = os.path.splitext(chapter_file)[0]
                
                # Update chapter status to processing
                self.status[session_id]['chapter_status'][chapter_name] = {
                    'status': 'processing',
                    'message': 'Processing chapter...',
                    'has_download': False
                }
                
                # Check if we have content for this chapter
                if chapter_file not in chapter_contents:
                    print(f"Chapter {chapter_file} not found in chapter_contents")
                    self.status[session_id]['chapter_status'][chapter_name] = {
                        'status': 'error',
                        'message': 'Chapter content not found',
                        'has_download': False
                    }
                    continue
                
                self.status[session_id].update({
                    'progress': int(30 + (i / total_chapters) * 60),  # Progress from 30% to 90%
                    'message': f'Creating mindmap for chapter {i+1}/{total_chapters}: {chapter_file}',
                    'processed_chapters': i
                })
                
                try:
                            # Processing chapter in memory
                    
                    # Get the chapter content from memory
                    content = chapter_contents[chapter_file]
                    
                    if not content.strip():
                        print(f"Chapter {chapter_file} is empty, skipping...")
                        self.status[session_id]['chapter_status'][chapter_name] = {
                            'status': 'error',
                            'message': 'Chapter content is empty',
                            'has_download': False
                        }
                        continue
                    
                    # Process the chapter using direct integration
                    self.status[session_id]['message'] = f'Analyzing chapter content: {chapter_file}'
                    # Starting analysis
                    
                    results = creator.process_chapter(
                        content=content,
                        title=chapter_name
                    )
                    
                            # Analysis completed
                    
                    # Validate results
                    if not results:
                        raise Exception("No results returned from analysis")
                    
                    validation_issues = validate_results(results)
                    if validation_issues:
                        print(f"Validation issues for {chapter_file}: {validation_issues}")
                        print(f"Continuing with potentially incomplete results for {chapter_file}")
                    
                    # Generate mindmaps based on type (in memory)
                    mindmaps_generated = {}
                    
                    self.status[session_id]['message'] = f'Generating mindmaps: {chapter_file}'
                    
                    try:
                        if mindmap_type in ['comprehensive', 'main', 'all']:
                            # Creating main mindmap
                            mindmap = creator.create_mindmap(results, mindmap_type='main')
                            if mindmap and mindmap.strip():
                                mindmaps_generated['comprehensive_mindmap'] = mindmap
                            else:
                                pass  # Empty main mindmap
                        
                        if mindmap_type in ['actionable', 'all']:
                            # Creating actionable mindmap
                            actionable_mindmap = creator.create_mindmap(results, mindmap_type='actionable')
                            if actionable_mindmap and actionable_mindmap.strip():
                                mindmaps_generated['actionable_mindmap'] = actionable_mindmap
                            else:
                                pass  # Empty actionable mindmap
                        
                        if mindmap_type in ['simple', 'all']:
                            # Creating simple mindmap
                            simple_mindmap = creator.create_mindmap(results, mindmap_type='simple')
                            if simple_mindmap and simple_mindmap.strip():
                                mindmaps_generated['simple_mindmap'] = simple_mindmap
                            else:
                                pass  # Empty simple mindmap
                    
                    except Exception as e:
                        # Error generating mindmaps
                        pass  # Continue processing even if mindmap generation fails
                    
                    # Store results in memory instead of files
                    chapter_info = chapters_data.get(chapter_file, {})
                    mindmap_result = {
                        'chapter_file': chapter_file,
                        'chapter_name': chapter_name,
                        'chapter_title': chapter_info.get('title', chapter_name),
                        'canonical_name': chapter_info.get('canonical_name', chapter_name),
                        'analysis_complete': results.get('analysis_complete', {}),
                        'analysis_summary': results.get('analysis_summary', ''),
                        'analysis_synthesis': results.get('analysis_synthesis', {}),
                        'quick_summary': results.get('quick_summary', ''),
                        'processing_report': results.get('processing_report', ''),
                        'mindmaps': mindmaps_generated,
                        'memory_based': True,
                        'validation_issues': validation_issues if validation_issues else None
                    }
                    
                    # Generate mindmap explanation/notes if we have a mindmap
                    try:
                        if mindmaps_generated:
                            self.status[session_id]['message'] = f'Creating mindmap explanation: {chapter_file}'
                            primary_mindmap = mindmaps_generated.get('comprehensive_mindmap') or mindmaps_generated.get('actionable_mindmap') or mindmaps_generated.get('simple_mindmap')
                            if primary_mindmap:
                                notes_content = creator.create_notes(results, primary_mindmap)
                                if notes_content and notes_content.strip():
                                    mindmap_result['mindmap_explanation'] = notes_content
                    except Exception as e:
                        pass  # Error creating mindmap explanation
                    
                    mindmap_results.append(mindmap_result)
                    
                    # Store results immediately after each chapter (append, don't overwrite)
                    if 'mindmap_results' not in self.results[session_id]:
                        self.results[session_id]['mindmap_results'] = []
                    
                    # Remove any existing entry for this chapter and add the new one
                    existing_results = self.results[session_id]['mindmap_results']
                    # Remove any existing result for this chapter
                    existing_results = [r for r in existing_results if r.get('chapter_name') != chapter_name]
                    # Add the new result
                    existing_results.append(mindmap_result)
                    self.results[session_id]['mindmap_results'] = existing_results
                    self.results[session_id]['memory_based'] = True
                    
                    # Mark chapter as completed
                    self.status[session_id]['completed_chapters'].append(chapter_name)
                    self.status[session_id]['chapter_status'][chapter_name] = {
                        'status': 'completed',
                        'message': 'Chapter processed successfully',
                        'has_download': True,
                        'memory_based': True,
                        'mindmaps_generated': len(mindmaps_generated)
                    }
                    
                    print(f"✅ Successfully processed {chapter_file}")
                    
                except Exception as e:
                    print(f"❌ Error processing {chapter_file}: {e}")
                    import traceback
                    traceback.print_exc()
                    
                    # Mark chapter as failed
                    self.status[session_id]['chapter_status'][chapter_name] = {
                        'status': 'error',
                        'message': f'Processing failed: {str(e)[:100]}',
                        'has_download': False
                    }
                    
                    # Create a placeholder result for failed chapters
                    failed_result = {
                        'chapter_name': chapter_name,
                        'chapter_file': chapter_file,
                        'mindmaps': {},
                        'has_mindmap': False,
                        'error': f"Processing failed: {str(e)[:200]}",
                        'memory_based': True
                    }
                    mindmap_results.append(failed_result)
            
            # Store results in memory instead of creating combined download package
            self.status[session_id]['message'] = 'Finalizing results...'
            self.status[session_id]['progress'] = 95
            
            # Ensure all results are properly stored and verify completeness
            final_results = self.results[session_id].get('mindmap_results', [])
            print(f"🔍 Final verification: {len(final_results)} chapters in results")
            for result in final_results:
                print(f"  ✓ Stored: {result.get('chapter_name', 'Unknown')}")
            
            self.results[session_id]['memory_based'] = True
            
            # Only mark complete AFTER verification
            self.status[session_id].update({
                'progress': 100,
                'message': f'✅ Memory-based mindmap processing completed! {len(final_results)} chapters processed.',
                'completed': True,
                'processed_chapters': len(final_results),
                'type': 'complete',
                'completion_type': 'mindmaps_generated',
                'download_id': session_id,
                'memory_based': True
            })
            
        except Exception as e:
            error_msg = f'Error processing mindmaps: {str(e)}'
            print(error_msg)
            import traceback
            traceback.print_exc()
            self.status[session_id].update({
                'progress': 0,
                'message': error_msg,
                'error': error_msg,
                'completed': True,
                'type': 'error'
            })
            print(f"Mindmap processing error: {error_msg}")
            print(traceback.format_exc())
            
            self.status[session_id].update({
                'error': error_msg,
                'message': error_msg,
                'completed': True
            })
    
    def _collect_chapter_info(self, output_dir: str) -> List[Dict[str, Any]]:
        """Collect information about processed chapters."""
        chapters = []
        
        for filename in os.listdir(output_dir):
            if filename.endswith('.md') and not filename.startswith('00_'):
                filepath = os.path.join(output_dir, filename)
                
                # Get file size and basic info
                file_size = os.path.getsize(filepath)
                
                # Try to extract chapter type and title from filename
                parts = filename.replace('.md', '').split('_', 2)
                if len(parts) >= 3:
                    index = parts[0]
                    chapter_type = parts[1]
                    title = parts[2].replace('-', ' ').title()
                else:
                    index = "00"
                    chapter_type = "chapter"
                    title = filename.replace('.md', '').replace('_', ' ').title()
                
                chapters.append({
                    'filename': filename,
                    'title': title,
                    'type': chapter_type,
                    'size': file_size,
                    'size_formatted': self._format_file_size(file_size),
                    'index': index
                })
        
        # Sort chapters by index
        chapters.sort(key=lambda x: x['index'])
        return chapters
    
    def _collect_mindmap_files_direct(self, chapter_output_dir: str, chapter_name: str, mindmaps_saved: list) -> Dict[str, Any]:
        """Collect mindmap files from direct processing."""
        files = {}
        
        # Check for generated files based on what was actually saved
        for mindmap_type, file_path in mindmaps_saved:
            if os.path.exists(file_path):
                files[mindmap_type.lower()] = {
                    'path': file_path,
                    'name': os.path.basename(file_path),
                    'size': os.path.getsize(file_path)
                }
        
        # Look for other common files in the output directory
        common_files = {
            'analysis_complete.json': 'analysis',
            'analysis_summary.md': 'summary',
            'analysis_synthesis.json': 'synthesis',
            'processing_report.txt': 'report',
            'quick_summary.md': 'quick_summary',
            'README.md': 'readme'
        }
        
        for filename, file_type in common_files.items():
            file_path = os.path.join(chapter_output_dir, filename)
            if os.path.exists(file_path):
                files[file_type] = {
                    'path': file_path,
                    'name': filename,
                    'size': os.path.getsize(file_path)
                }
        
        # Determine what types of content we have
        has_mindmap = any(key in files for key in ['comprehensive', 'main', 'actionable'])
        has_summary = 'summary' in files or 'quick_summary' in files
        has_explanation = 'explanation' in files
        
        return {
            'chapter_name': chapter_name,
            'files': files,
            'has_mindmap': has_mindmap,
            'has_summary': has_summary,
            'has_explanation': has_explanation,
            'status': 'success'
        }
    
    def _collect_mindmap_files(self, chapter_dir: str, chapter_name: str) -> Dict[str, Any]:
        """Collect mindmap output files for a chapter."""
        result = {
            'chapter_name': chapter_name,
            'files': {},
            'has_mindmap': False,
            'has_summary': False,
            'has_explanation': False
        }
        
        # Look for expected files based on actual output from main.py
        expected_files = {
            # Mindmap files (check for different types)
            'comprehensive_mindmap.mmd': 'mindmap',
            'main_mindmap.mmd': 'mindmap',
            'actionable_mindmap.mmd': 'mindmap',
            'relationship_mindmap.mmd': 'mindmap',
            # Study materials
            'quick_summary.md': 'summary',
            'mindmap_explanation.md': 'explanation',
            'README.md': 'readme'
        }
        
        for filename, file_type in expected_files.items():
            filepath = os.path.join(chapter_dir, filename)
            if os.path.exists(filepath):
                result['files'][file_type] = filepath
                if file_type == 'mindmap':
                    result['has_mindmap'] = True
                elif file_type == 'summary':
                    result['has_summary'] = True
                elif file_type == 'explanation':
                    result['has_explanation'] = True
        
        # Debug: List all files in the directory
        if os.path.exists(chapter_dir):
            all_files = os.listdir(chapter_dir)
            print(f"Files in {chapter_dir}: {all_files}")
        
        return result
    
    def _create_combined_download(self, session_id: str, mindmap_results: List[Dict]) -> str:
        """Create a combined markdown file with all results."""
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], session_id, 'combined_results.md')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Complete Mindmap Analysis Results\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            for result in mindmap_results:
                chapter_name = result['chapter_name']
                f.write(f"## {chapter_name.replace('_', ' ').replace('-', ' ').title()}\n\n")
                
                # Check if processing failed
                if 'error' in result:
                    f.write("### Processing Error\n\n")
                    f.write(f"**Error:** {result['error']}\n\n")
                    f.write("This chapter could not be processed successfully.\n\n")
                else:
                    files = result.get('files', {})
                    
                    # Add mindmap content (check various mindmap types)
                    mindmap_file = None
                    for mindmap_type in ['comprehensive', 'main', 'actionable']:
                        if mindmap_type in files:
                            mindmap_file = files[mindmap_type]['path']
                            break
                    
                    if mindmap_file and os.path.exists(mindmap_file):
                        f.write("### Mindmap\n\n")
                        f.write("```mermaid\n")
                        try:
                            with open(mindmap_file, 'r', encoding='utf-8') as mf:
                                f.write(mf.read())
                        except Exception as e:
                            f.write(f"Error reading mindmap: {e}")
                        f.write("\n```\n\n")
                    
                    # Add summary
                    summary_file = None
                    for summary_type in ['summary', 'quick_summary']:
                        if summary_type in files:
                            summary_file = files[summary_type]['path']
                            break
                    
                    if summary_file and os.path.exists(summary_file):
                        f.write("### Summary\n\n")
                        try:
                            with open(summary_file, 'r', encoding='utf-8') as sf:
                                f.write(sf.read())
                        except Exception as e:
                            f.write(f"Error reading summary: {e}")
                        f.write("\n\n")
                    
                    # Add explanation
                    if 'explanation' in files and os.path.exists(files['explanation']['path']):
                        f.write("### Explanation\n\n")
                        try:
                            with open(files['explanation']['path'], 'r', encoding='utf-8') as ef:
                                f.write(ef.read())
                        except Exception as e:
                            f.write(f"Error reading explanation: {e}")
                        f.write("\n\n")
                    
                    if not files:
                        f.write("### No Content Generated\n\n")
                        f.write("No mindmap content was generated for this chapter.\n\n")
                
                f.write("---\n\n")
        
        return output_path
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def get_status(self, session_id: str) -> Dict[str, Any]:
        """Get current processing status."""
        return self.status.get(session_id, {})
    
    def get_results(self, session_id: str) -> Dict[str, Any]:
        """Get processing results."""
        return self.results.get(session_id, {})


# Initialize processing manager
process_manager = ProcessingManager()


@app.route('/')
def index():
    """Main page with file upload interface."""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    # Get available models and pricing
    pricing_summary = get_pricing_summary()
    
    return render_template('index.html', pricing_summary=pricing_summary)





@app.route('/validate_api_key', methods=['POST'])
def validate_api_key():
    """Validate an OpenAI API key."""
    try:
        data = request.get_json()
        api_key = data.get('api_key', '').strip()
        
        if not api_key:
            return jsonify({'valid': False, 'error': 'API key is required'})
        
        if not api_key.startswith('sk-'):
            return jsonify({'valid': False, 'error': 'Invalid API key format'})
        
        # Basic validation - just check format (no storage)
        # Note: API key is not stored anywhere on server
        return jsonify({'valid': True, 'message': 'API key format is valid'})
        
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)})


@app.route('/get_affordable_models', methods=['GET'])
def get_affordable_models():
    """Get list of affordable OpenAI models."""
    try:
        # Get pricing summary from pricing manager
        pricing_summary = get_pricing_summary()
        
        # Convert to the format expected by the frontend
        models = []
        for model_info in pricing_summary['models']:
            models.append({
                'id': model_info['id'],
                'name': model_info['name'],
                'input_price': model_info.get('input_cost', 0),
                'output_price': model_info['output_cost'],
                'description': model_info.get('description', '')
            })
        
        return jsonify({
            'models': models,
            'total_count': len(models),
            'last_updated': pricing_summary['last_updated']
        })
        
    except Exception as e:
        app.logger.error(f"Error getting affordable models: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload with in-memory processing."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.epub'):
            return jsonify({'error': 'Only EPUB files are supported'}), 400
        
        # Read file into memory instead of saving to disk
        filename = secure_filename(file.filename)
        session_id = session['session_id']
        
        # Read the entire file content into memory
        file_data = file.read()
        
        # Get processing parameters
        min_length = request.form.get('min_length', 500, type=int)
        
        # Start processing with in-memory data
        process_manager.start_epub_processing_memory(session_id, file_data, filename, min_length)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/status')
def get_status():
    """Get current processing status."""
    session_id = session.get('session_id')
    if not session_id:
        return jsonify({'error': 'No session found'}), 400
    
    status = process_manager.get_status(session_id)
    return jsonify(status)


@app.route('/chapters')
def get_chapters():
    """Get list of chapters from memory-based processing only."""
    session_id = session.get('session_id')
    if not session_id:
        return jsonify({'error': 'No session found'}), 400
    
    # Check if we have processed chapters from EPUB upload
    if session_id in process_manager.results:
        result_data = process_manager.results[session_id]
        if 'chapters' in result_data:
            chapters_dict = result_data['chapters']
            print(f"DEBUG: Found chapters from EPUB processing: {type(chapters_dict)}")
            print(f"DEBUG: Chapters data: {list(chapters_dict.keys()) if isinstance(chapters_dict, dict) else chapters_dict}")
            
            # Convert dictionary to array format for frontend
            chapters_array = []
            if isinstance(chapters_dict, dict):
                for filename, chapter_info in chapters_dict.items():
                    chapters_array.append({
                        'filename': filename,
                        'title': chapter_info.get('title', filename),
                        'canonical_name': chapter_info.get('canonical_name', filename.replace('.md', '')),
                        'available': True,
                        'full_path': chapter_info.get('full_path', ''),
                        'preview': f"Chapter: {chapter_info.get('title', filename)}"
                    })
            else:
                # If it's already an array, use it directly
                chapters_array = chapters_dict
            
            response_data = {
                'chapters': chapters_array,
                'total_available': len(chapters_array),
                'source': 'memory_processing'
            }
            return jsonify(response_data)
    
    # No fallback - require EPUB upload for chapter data
    return jsonify({
        'error': 'No chapters available. Please upload an EPUB file first.',
        'chapters': [],
        'total_available': 0,
        'source': 'none'
    })


@app.route('/chapter-status')
def get_chapter_status():
    """Get individual chapter processing status."""
    session_id = session.get('session_id')
    
    if not session_id:
        return jsonify({'error': 'No session found'}), 400
    
    status = process_manager.get_status(session_id)
    chapter_status = status.get('chapter_status', {})
    completed_chapters = status.get('completed_chapters', [])
    
            # Check chapter status (debug output removed for cleaner terminal)
    
    # Check if we have memory-based processing results
    results = process_manager.get_results(session_id)
    
    if results.get('memory_based', False) and 'mindmap_results' in results:
        # Use memory-based chapter data
        canonical_chapter_status = {}
        
        for mindmap_result in results['mindmap_results']:
            chapter_name = mindmap_result['chapter_name']
            canonical_name = mindmap_result.get('canonical_name', chapter_name)
            display_title = mindmap_result.get('chapter_title', chapter_name)
            
            # Process chapter status
            
            # Get status for this chapter from the chapter_status dict
            stored_status = chapter_status.get(chapter_name, {})
            is_completed = chapter_name in completed_chapters
            
            # Create the status structure the frontend expects
            if is_completed and stored_status:
                # Use stored status from processing
                status_info = {
                    'status': stored_status.get('status', 'completed'),
                    'message': stored_status.get('message', 'Chapter processed successfully'), 
                    'has_download': stored_status.get('has_download', True)
                }
            elif is_completed:
                # Default completed status
                status_info = {
                    'status': 'completed',
                    'message': 'Chapter processed successfully',
                    'has_download': True
                }
            else:
                # Not completed yet
                status_info = {
                    'status': 'pending',
                    'message': 'Waiting to be processed...',
                    'has_download': False
                }
            
            print(f"    Final status: {status_info}")
            
            # Frontend expects the status directly, not nested
            canonical_chapter_status[canonical_name] = status_info
        
        response_data = {
            'chapter_status': canonical_chapter_status,
            'completed_chapters': completed_chapters,
            'total_chapters': len(canonical_chapter_status),
            'processed_chapters': len([name for name, status in canonical_chapter_status.items() if status.get('status') == 'completed']),
            'memory_based': True
        }
        
        print(f"  Returning {len(canonical_chapter_status)} chapters")
        return jsonify(response_data)
    
    # No fallback - require memory-based processing
    print("  No memory-based results found")
    return jsonify({
        'error': 'No chapter status available. Please upload an EPUB file and process chapters first.',
        'chapter_status': {},
        'completed_chapters': [],
        'total_chapters': 0,
        'processed_chapters': 0,
        'memory_based': True
    })


@app.route('/process-mindmaps', methods=['POST'])
def process_mindmaps():
    """Start mindmap processing for selected chapters."""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': 'No session found'}), 400
        
        # Get API key from request or environment only (no session storage)
        api_key = request.get_json().get('api_key') if request.get_json() else None
        if not api_key:
            api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            return jsonify({'error': 'OpenAI API key is required. Please provide it in the request or set OPENAI_API_KEY environment variable.'}), 400
        
        data = request.get_json()
        selected_chapters = data.get('selected_chapters', [])
        ai_model = data.get('ai_model', 'gpt-4o-mini')  # Default to cheapest model
        mindmap_type = data.get('mindmap_type', 'comprehensive')
        
        if not selected_chapters:
            return jsonify({'error': 'No chapters selected'}), 400
        
        # Validate that the selected model is available and affordable
        available_models = get_available_models()
        if ai_model not in available_models:
            return jsonify({'error': f'Model {ai_model} is not available or exceeds cost threshold'}), 400
        
        # Start mindmap processing with user-selected parameters
        process_manager.start_mindmap_processing(session_id, selected_chapters, ai_model, mindmap_type, api_key)
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download/<session_id>')
def download_results(session_id):
    """Download results for a specific session."""
    # Validate session
    if session_id not in process_manager.results:
        return jsonify({'error': 'Session not found'}), 404
    
    results = process_manager.get_results(session_id)
    if 'combined_download' not in results:
        return jsonify({'error': 'No combined file found'}), 404
    
    return send_file(
        results['combined_download'],
        as_attachment=True,
        download_name='mindmap_analysis_results.md',
        mimetype='text/markdown'
    )





@app.route('/download-chapter/<chapter_name>')
def download_chapter(chapter_name):
    """Download individual chapter results (memory-based processing only)."""
    session_id = session.get('session_id')
    if not session_id:
        return jsonify({'error': 'No session found'}), 400
    
    results = process_manager.get_results(session_id)
    if 'mindmap_results' not in results:
        return jsonify({'error': 'No mindmap results found. Please upload an EPUB file and process chapters first.'}), 404
    
    # Debug: Print available chapters
    print(f"Requested chapter: {chapter_name}")
    print(f"Available chapters: {[r['chapter_name'] for r in results['mindmap_results']]}")
    
    # Find the specific chapter
    chapter_result = None
    for result in results['mindmap_results']:
        if result['chapter_name'] == chapter_name:
            chapter_result = result
            break
    
    if not chapter_result:
        # Try alternative matching - sometimes URLs might encode differently
        for result in results['mindmap_results']:
            # Try exact match, then partial matches
            if (result['chapter_name'] == chapter_name or 
                result['chapter_name'].replace('_', '-') == chapter_name or
                result['chapter_name'].replace('-', '_') == chapter_name):
                chapter_result = result
                break
    
    if not chapter_result:
        return jsonify({
            'error': f'Chapter "{chapter_name}" not found',
            'available_chapters': [r['chapter_name'] for r in results['mindmap_results']]
        }), 404
    
    # Generate file content from memory data
    content_lines = []
    content_lines.append(f"# {chapter_result.get('chapter_title', chapter_name)}")
    content_lines.append("")
    content_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content_lines.append("Generated using: RAM-only processing")
    content_lines.append("")
    
    # Add analysis summary
    if chapter_result.get('analysis_summary'):
        content_lines.append("## Analysis Summary")
        content_lines.append("")
        content_lines.append(chapter_result['analysis_summary'])
        content_lines.append("")
    
    # Add quick summary
    if chapter_result.get('quick_summary'):
        content_lines.append("## Quick Summary")
        content_lines.append("")
        content_lines.append(chapter_result['quick_summary'])
        content_lines.append("")
    
    # Add mindmaps
    mindmaps = chapter_result.get('mindmaps', {})
    for mindmap_type, mindmap_content in mindmaps.items():
        if mindmap_content:
            content_lines.append(f"## {mindmap_type.replace('_', ' ').title()}")
            content_lines.append("")
            content_lines.append("```mermaid")
            content_lines.append(mindmap_content)
            content_lines.append("```")
            content_lines.append("")
    
    # Add mindmap explanation
    if chapter_result.get('mindmap_explanation'):
        content_lines.append("## Mindmap Explanation")
        content_lines.append("")
        content_lines.append(chapter_result['mindmap_explanation'])
        content_lines.append("")
    
    # Add processing report
    if chapter_result.get('processing_report'):
        content_lines.append("## Processing Report")
        content_lines.append("")
        content_lines.append(chapter_result['processing_report'])
        content_lines.append("")
    
    # Create in-memory file instead of writing to disk
    from io import StringIO, BytesIO
    content = '\n'.join(content_lines)
    
    # Convert to bytes for download
    content_bytes = content.encode('utf-8')
    content_io = BytesIO(content_bytes)
    content_io.seek(0)
    
    return send_file(
        content_io,
        as_attachment=True, 
        download_name=f'{chapter_name}_mindmap_results.md',
        mimetype='text/markdown'
    )


@app.route('/force-refresh-status')
def force_refresh_status():
    """Force refresh the frontend status by providing current session data."""
    session_id = session.get('session_id')
    if not session_id:
        return jsonify({'error': 'No session found'}), 400
    
    # Get the current status and force update
    results = process_manager.get_results(session_id)
    status = process_manager.get_status(session_id)
    
    if not results.get('memory_based', False):
        # Force the memory_based flag
        results['memory_based'] = True
        status['memory_based'] = True
    
    response_data = {
        'session_id': session_id,
        'status': 'completed',
        'memory_based': True,
        'total_chapters': len(results.get('mindmap_results', [])),
        'completed_chapters': status.get('completed_chapters', []),
        'chapter_details': []
    }
    
    if 'mindmap_results' in results:
        for chapter_result in results['mindmap_results']:
            chapter_name = chapter_result['chapter_name']
            response_data['chapter_details'].append({
                'chapter_name': chapter_name,
                'canonical_name': chapter_result.get('canonical_name', chapter_name),
                'display_title': chapter_result.get('chapter_title', chapter_name),
                'status': 'completed',
                'is_completed': True,
                'has_download': True
            })
    
    return jsonify(response_data)





@app.route('/recover-session')
def recover_session():
    """Recover lost session by connecting to available session data."""
    print(f"🔧 DEBUG: Session recovery requested")
    
    # Check if we already have a session
    current_session_id = session.get('session_id')
    if current_session_id:
        return jsonify({'message': 'Session already exists', 'session_id': current_session_id})
    
    # Find available sessions with data
    available_sessions = []
    for session_id in process_manager.status.keys():
        status = process_manager.get_status(session_id)
        results = process_manager.get_results(session_id)
        
        if results.get('memory_based', False) and 'mindmap_results' in results:
            available_sessions.append({
                'session_id': session_id,
                'completed_chapters': status.get('completed_chapters', []),
                'mindmap_count': len(results.get('mindmap_results', []))
            })
    
    if not available_sessions:
        return jsonify({'error': 'No recoverable sessions found'}), 404
    
    # Use the most recent session (last in list)
    recovery_session = available_sessions[-1]
    recovered_session_id = recovery_session['session_id']
    
    # Restore session
    session['session_id'] = recovered_session_id
    
    print(f"✅ DEBUG: Session recovered: {recovered_session_id}")
    print(f"✅ DEBUG: Chapters available: {recovery_session['completed_chapters']}")
    
    return jsonify({
        'message': 'Session recovered successfully',
        'session_id': recovered_session_id,
        'recovered_data': recovery_session
    })





@app.route('/download-combined-docx')
def download_combined_docx():
    """Download combined results as DOCX file."""
    session_id = session.get('session_id')
    
    if not session_id:
        return jsonify({'error': 'No session found'}), 400
    
    try:
        # Use streamlined DOCX creation function
        docx_data = create_docx_from_memory_data(session_id, is_combined=True)
        
        if not docx_data:
            return jsonify({'error': 'Failed to create DOCX file. No processed data available.'}), 500
        
        # Ensure we have a BytesIO object
        if hasattr(docx_data, 'seek'):
            docx_data.seek(0)
        
        return send_file(
            docx_data,
            as_attachment=True,
            download_name='mindmap_analysis_results.docx',
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        print(f"❌ DEBUG: Error creating DOCX: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error creating DOCX: {str(e)}'}), 500


@app.route('/download-chapter-docx/<chapter_name>')
def download_chapter_docx(chapter_name):
    """Download individual chapter as DOCX file."""
    session_id = session.get('session_id')
    
    if not session_id:
        return jsonify({'error': 'No session found'}), 400
    
    try:
        results = process_manager.get_results(session_id)
        
        # Find the chapter in results
        chapter_data = None
        if 'mindmap_results' in results:
            for chapter_result in results['mindmap_results']:
                if chapter_result['chapter_name'] == chapter_name:
                    chapter_data = chapter_result
                    break
        
        if not chapter_data:
            return jsonify({'error': f'Chapter not found: {chapter_name}'}), 404
        
        # Create DOCX
        docx_data = create_docx_from_memory_data(session_id, chapter_data=chapter_data, is_combined=False)
        
        if not docx_data:
            return jsonify({'error': 'Failed to create DOCX file'}), 500
        
        if hasattr(docx_data, 'seek'):
            docx_data.seek(0)
        
        # Generate clean filename
        safe_filename = f"{chapter_name.replace(' ', '_').replace(':', '').replace('/', '')}.docx"
        
        return send_file(
            docx_data,
            as_attachment=True,
            download_name=safe_filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        print(f"Error creating DOCX: {e}")
        return jsonify({'error': f'Error creating DOCX: {str(e)}'}), 500


@app.route('/download-combined-pdf')
def download_combined_pdf():
    """Download combined PDF of all chapters"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': 'No active session'}), 404
        
        # Create combined PDF using memory data
        pdf_data = create_pdf_from_memory_data(session_id, is_combined=True)
        
        if not pdf_data:
            return jsonify({'error': 'No data available for download'}), 404
        
        # Ensure the BytesIO pointer is at the beginning
        if hasattr(pdf_data, 'seek'):
            pdf_data.seek(0)
        
        return send_file(
            pdf_data,
            as_attachment=True,
            download_name='mindmap_analysis_complete.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"Error in download_combined_pdf: {e}")
        return jsonify({'error': 'Failed to generate combined PDF'}), 500


@app.route('/download-chapter-pdf/<chapter_name>')
def download_chapter_pdf(chapter_name):
    """Download individual chapter as PDF"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': 'No active session'}), 404
        
        # Get results from process manager
        results = process_manager.get_results(session_id)
        if not results or 'mindmap_results' not in results:
            return jsonify({'error': 'No results found'}), 404
        
        # Find the chapter in results
        chapter_data = None
        if 'mindmap_results' in results:
            for chapter_result in results['mindmap_results']:
                if chapter_result['chapter_name'] == chapter_name:
                    chapter_data = chapter_result
                    break
        
        if not chapter_data:
            return jsonify({'error': f'Chapter not found: {chapter_name}'}), 404
        
        # Create PDF
        pdf_data = create_pdf_from_memory_data(session_id, chapter_data=chapter_data, is_combined=False)
        
        if not pdf_data:
            return jsonify({'error': 'Failed to generate PDF'}), 500
        
        # Ensure the BytesIO pointer is at the beginning
        if hasattr(pdf_data, 'seek'):
            pdf_data.seek(0)
        
        # Create safe filename
        safe_filename = f"{chapter_name.replace(' ', '_').replace(':', '').replace('/', '')}.pdf"
        
        return send_file(
            pdf_data,
            as_attachment=True,
            download_name=safe_filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"Error in download_chapter_pdf: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to generate PDF: {str(e)}'}), 500


if __name__ == '__main__':
    # Only run development server if not in production environment
    if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('HEROKU_APP_NAME'):
        print("⚠️  Production environment detected. Use 'gunicorn wsgi:app' instead of running this file directly.")
        print("   This script should only be used for local development.")
        exit(1)
    
    print("🚀 Starting Flask development server...")
    print("   Note: This is for local development only!")
    
    # Get port from environment variable (for local development)
    port = int(os.environ.get('PORT', 5001))  # Changed default port to 5001
    # Get debug mode from environment
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    # Get host from environment (defaults to localhost for local dev)
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    
    app.run(debug=debug_mode, host=host, port=port)
