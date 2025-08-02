"""
Simple, unified PDF creator for Mind Map Framework - FIXED VERSION
Leverages existing data structure from DOCX creator with minimal changes.
"""

import os
import io
import base64
import requests
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black, darkblue
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

# Import the existing functions from DOCX creator to reuse logic
from simple_docx_creator import (
    _format_chapter_title,
    _clean_markdown_remnants,
    _generate_mindmap_image
)


def create_pdf(chapters, output_path=None):
    """
    UNIFIED PDF creation function - handles both single and multiple chapters!
    
    Args:
        chapters: Either:
                 - Single chapter: (chapter_name, chapter_data) tuple
                 - Multiple chapters: dict of {chapter_name: chapter_data}
        output_path: Where to save (if None, returns BytesIO)
    
    Returns:
        Path to saved file or BytesIO object
    """
    # Create PDF buffer
    if output_path:
        doc = SimpleDocTemplate(output_path, pagesize=A4)
    else:
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
    
    # Setup styles
    styles = _setup_pdf_styles()
    story = []
    
    # Normalize input to handle both single and multiple chapters
    if isinstance(chapters, tuple) and len(chapters) == 2:
        # Single chapter: (chapter_name, chapter_data)
        chapter_name, chapter_data = chapters
        chapters_dict = {chapter_name: chapter_data}
        is_single_chapter = True
    elif isinstance(chapters, dict):
        # Multiple chapters: {chapter_name: chapter_data}
        chapters_dict = chapters
        is_single_chapter = len(chapters_dict) == 1
    else:
        raise ValueError("chapters must be either (chapter_name, chapter_data) tuple or {chapter_name: chapter_data} dict")
    
    if is_single_chapter:
        # Single chapter document
        chapter_name, chapter_data = next(iter(chapters_dict.items()))
        clean_title = _format_chapter_title(chapter_name, chapter_data)
        
        # Add title
        story.append(Paragraph(clean_title, styles['DocTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Add chapter content
        _add_chapter_content_to_pdf(story, chapter_data, chapter_name, styles)
    else:
        # Multi-chapter document
        # Add main document title
        story.append(Paragraph("Mind Map Analysis Report", styles['DocTitle']))
        story.append(Spacer(1, 0.5*inch))
        
        # Add each chapter
        for i, (chapter_name, chapter_data) in enumerate(chapters_dict.items()):
            clean_title = _format_chapter_title(chapter_name, chapter_data)
            
            # Chapter title
            story.append(Paragraph(clean_title, styles['ChapterHeading']))
            story.append(Spacer(1, 0.2*inch))
            
            # Add chapter content
            _add_chapter_content_to_pdf(story, chapter_data, chapter_name, styles)
            
            # Add page break between chapters (but not after the last one)
            if i < len(chapters_dict) - 1:
                story.append(PageBreak())
    
    # Build PDF
    doc.build(story)
    
    # Return result
    if output_path:
        return output_path
    else:
        pdf_buffer.seek(0)
        return pdf_buffer


def _setup_pdf_styles():
    """Setup PDF styles with professional formatting"""
    styles = getSampleStyleSheet()
    
    # Create completely unique styles with simple names
    styles.add(ParagraphStyle(
        name='DocTitle',
        parent=styles['Normal'],
        fontSize=20,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=darkblue,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='ChapterHeading',
        parent=styles['Normal'],
        fontSize=16,
        spaceAfter=20,
        spaceBefore=20,
        textColor=darkblue,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='SectionHeading',
        parent=styles['Normal'],
        fontSize=14,
        spaceAfter=15,
        spaceBefore=15,
        textColor=black,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='MindMapBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        alignment=TA_JUSTIFY,
        leftIndent=0,
        rightIndent=0,
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        name='MindMapBullet',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        leftIndent=0.25*inch,
        fontName='Helvetica'
    ))
    
    return styles


def _add_chapter_content_to_pdf(story, chapter_data, chapter_name, styles):
    """
    Add a chapter's content to PDF story.
    
    Args:
        story: PDF story list to append to
        chapter_data: Dictionary with chapter analysis data
        chapter_name: Name of the chapter
        styles: PDF styles dictionary
    """
    # Add mindmap section
    mindmaps = chapter_data.get('mindmaps', {})
    comprehensive_mindmap = mindmaps.get('comprehensive_mindmap') if mindmaps else None
    
    if comprehensive_mindmap:
        _add_mindmap_section_to_pdf(story, comprehensive_mindmap, styles)
    else:
        # Check if mindmap is stored at top level (wrong structure)
        if 'comprehensive_mindmap' in chapter_data:
            _add_mindmap_section_to_pdf(story, chapter_data['comprehensive_mindmap'], styles)
    
    # Add explanation section  
    if chapter_data.get('mindmap_explanation'):
        _add_explanation_section_to_pdf(story, chapter_data['mindmap_explanation'], styles)
    
    # Add summary section
    if chapter_data.get('quick_summary'):
        _add_summary_section_to_pdf(story, chapter_data['quick_summary'], styles)
    
    # Add detailed analysis
    if chapter_data.get('analysis_summary'):
        _add_analysis_section_to_pdf(story, chapter_data['analysis_summary'], styles)


def _add_mindmap_section_to_pdf(story, mindmap_content, styles):
    """Add mindmap section to PDF with image or text fallback"""
    # Section heading
    story.append(Paragraph("Mind Map", styles['SectionHeading']))
    
    # Try to generate and add mindmap image
    image_added = False
    try:
        # Use the same image generation logic as DOCX creator
        image_data = _generate_mindmap_image(mindmap_content)
        
        if image_data:
            # Add image to PDF
            image_stream = io.BytesIO(image_data)
            img = Image(image_stream, width=6*inch, height=4*inch)
            story.append(img)
            story.append(Spacer(1, 0.2*inch))
            image_added = True
            
    except Exception as e:
        print(f"✗ Error adding mindmap image to PDF: {e}")
    
    # Add text fallback if image failed
    if not image_added:
        print("📝 Adding mindmap text fallback to PDF")
        story.append(Paragraph("Note: Mindmap visualization not available. The mindmap structure is shown below:", styles['MindMapBody']))
        story.append(Spacer(1, 0.1*inch))
        
        # Add the mindmap content as preformatted text
        mindmap_text = str(mindmap_content).replace('<', '&lt;').replace('>', '&gt;')
        story.append(Paragraph(f"<pre>{mindmap_text}</pre>", styles['MindMapBody']))
    
    story.append(Spacer(1, 0.2*inch))


def _add_explanation_section_to_pdf(story, explanation_content, styles):
    """Add explanation section to PDF with proper formatting"""
    cleaned_content = _clean_markdown_remnants(explanation_content)
    
    story.append(Paragraph("Mind Map Explanation", styles['SectionHeading']))
    _add_formatted_content_to_pdf(story, cleaned_content, styles)


def _add_summary_section_to_pdf(story, summary_content, styles):
    """Add summary section to PDF with proper formatting"""
    cleaned_content = _clean_markdown_remnants(summary_content)
    
    story.append(Paragraph("Comprehensive Summary", styles['SectionHeading']))
    _add_formatted_content_to_pdf(story, cleaned_content, styles)


def _add_analysis_section_to_pdf(story, analysis_content, styles):
    """Add detailed analysis section to PDF with proper formatting"""
    story.append(Paragraph("Detailed Analysis", styles['SectionHeading']))
    _add_formatted_content_to_pdf(story, analysis_content, styles)


def _add_formatted_content_to_pdf(story, content, styles):
    """Convert markdown-style content to properly formatted PDF content"""
    if not content:
        return
        
    content_str = str(content)
    lines = content_str.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.1*inch))
            continue
            
        # Skip horizontal rules completely
        if line in ['---', '===', '***', '___']:
            continue
            
        # Handle different markdown elements
        if line.startswith('###'):
            # Sub-sub heading
            text = line.replace('###', '').strip()
            story.append(Paragraph(text, styles['SectionHeading']))
            
        elif line.startswith('##'):
            # Sub heading  
            text = line.replace('##', '').strip()
            story.append(Paragraph(text, styles['SectionHeading']))
            
        elif line.startswith('#'):
            # Main heading
            text = line.replace('#', '').strip()
            story.append(Paragraph(text, styles['ChapterHeading']))
            
        elif line.startswith('- ') or line.startswith('* '):
            # Bullet point
            text = '• ' + line[2:].strip()
            story.append(Paragraph(text, styles['MindMapBullet']))
            
        elif line.startswith('**') and line.endswith('**') and line.count('**') == 2:
            # Bold text (entire line)
            text = line.replace('**', '')
            story.append(Paragraph(f"<b>{text}</b>", styles['MindMapBody']))
            
        elif ':' in line and len(line.split(':')) == 2:
            # Key-value pairs (often in summaries)
            key, value = line.split(':', 1)
            text = f"<b>{key.strip()}:</b> {value.strip()}"
            story.append(Paragraph(text, styles['MindMapBody']))
            
        else:
            # Regular paragraph with potential inline formatting
            formatted_text = _format_inline_text_for_pdf(line)
            story.append(Paragraph(formatted_text, styles['MindMapBody']))


def _format_inline_text_for_pdf(text):
    """Format inline text for PDF (handle bold, etc.)"""
    import re
    
    # Replace **bold** with <b>bold</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    
    # Replace *italic* with <i>italic</i>
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    
    # Escape HTML characters
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    
    # Restore our formatting tags
    text = text.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
    text = text.replace('&lt;i&gt;', '<i>').replace('&lt;/i&gt;', '</i>')
    
    return text


# Legacy compatibility functions
def create_chapter_pdf_direct(chapter_data, chapter_name, output_path=None):
    """Legacy compatibility wrapper for single chapter PDF creation"""
    return create_pdf((chapter_name, chapter_data), output_path)


def create_combined_pdf_direct(all_chapters_data, output_path=None):
    """Legacy compatibility wrapper for combined chapter PDF creation"""
    return create_pdf(all_chapters_data, output_path)