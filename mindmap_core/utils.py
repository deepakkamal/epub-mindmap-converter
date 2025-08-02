"""
Utility functions for the Mind Map Creator
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

def save_results(results: Dict[str, Any], output_dir: Path, filename_prefix: str = "analysis") -> Dict[str, Path]:
    """
    Save analysis results to files
    
    Args:
        results: Results dictionary from analysis
        output_dir: Directory to save files
        filename_prefix: Prefix for filenames
        
    Returns:
        Dictionary mapping file types to saved paths
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    saved_files = {}
    
    # Save complete results as JSON
    json_file = output_dir / f"{filename_prefix}_complete.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    saved_files['complete_json'] = json_file
    
    # Save synthesis separately
    if 'synthesis' in results:
        synthesis_file = output_dir / f"{filename_prefix}_synthesis.json"
        with open(synthesis_file, 'w', encoding='utf-8') as f:
            json.dump(results['synthesis'], f, indent=2, ensure_ascii=False)
        saved_files['synthesis_json'] = synthesis_file
    
    # Save summary as markdown
    summary_file = output_dir / f"{filename_prefix}_summary.md"
    summary_content = create_summary_markdown(results)
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    saved_files['summary_md'] = summary_file
    
    logger.info(f"Results saved to {len(saved_files)} files in {output_dir}")
    return saved_files

def save_mindmap(mindmap_content: str, output_dir: Path, filename: str = "mindmap.mmd") -> Path:
    """
    Save mind map to file
    
    Args:
        mindmap_content: Mermaid mind map content
        output_dir: Directory to save file
        filename: Filename for the mind map
        
    Returns:
        Path to saved file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    mindmap_file = output_dir / filename
    with open(mindmap_file, 'w', encoding='utf-8') as f:
        f.write(mindmap_content)
    
    logger.info(f"Mind map saved to {mindmap_file}")
    return mindmap_file

def save_mindmap_notes(notes_content: str, output_dir: Path, filename: str = "mindmap_notes.md") -> Path:
    """
    Save mind map explanatory notes to file
    
    Args:
        notes_content: Explanatory notes content
        output_dir: Directory to save file
        filename: Filename for the notes
        
    Returns:
        Path to saved file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    notes_file = output_dir / filename
    with open(notes_file, 'w', encoding='utf-8') as f:
        f.write(notes_content)
    
    logger.info(f"Mind map notes saved to {notes_file}")
    return notes_file

def create_summary_markdown(results: Dict[str, Any]) -> str:
    """
    Create a markdown summary from results
    
    Args:
        results: Analysis results
        
    Returns:
        Markdown formatted summary
    """
    metadata = results.get('metadata', {})
    synthesis = results.get('synthesis', {})
    
    title = metadata.get('title', 'Document Analysis')
    
    md_content = f"""# Analysis Summary: {title}

## Main Themes

"""
    
    # Add main themes
    themes = synthesis.get('main_themes', [])
    for i, theme in enumerate(themes, 1):
        theme_text = extract_text_from_item(theme)
        md_content += f"{i}. {theme_text}\n"
    
    md_content += "\n## Key Principles\n\n"
    
    # Add key principles
    principles = synthesis.get('key_principles', [])
    for i, principle in enumerate(principles, 1):
        principle_text = extract_text_from_item(principle)
        md_content += f"{i}. {principle_text}\n"
    
    md_content += "\n## Critical Insights\n\n"
    
    # Add critical insights
    insights = synthesis.get('critical_insights', [])
    for i, insight in enumerate(insights, 1):
        insight_text = extract_text_from_item(insight)
        md_content += f"{i}. {insight_text}\n"
    
    md_content += "\n## Actionable Takeaways\n\n"
    
    # Add actionable takeaways
    takeaways = synthesis.get('actionable_takeaways', [])
    for i, takeaway in enumerate(takeaways, 1):
        takeaway_text = extract_text_from_item(takeaway)
        md_content += f"{i}. {takeaway_text}\n"
    
    return md_content

def extract_text_from_item(item: Any) -> str:
    """
    Extract readable text from various item formats
    
    Args:
        item: Item to extract text from
        
    Returns:
        Readable text string
    """
    if isinstance(item, dict):
        # Try common text fields
        for field in ['description', 'text', 'content', 'summary', 'name']:
            if field in item:
                return str(item[field])
        # Fallback to string representation
        return str(item)
    elif isinstance(item, str):
        return item
    else:
        return str(item)

def estimate_reading_time(text: str) -> int:
    """
    Estimate reading time in minutes
    
    Args:
        text: Text to estimate reading time for
        
    Returns:
        Estimated reading time in minutes
    """
    words = len(text.split())
    # Average reading speed: 200-250 words per minute
    return max(1, round(words / 225))

def validate_results(results: Dict[str, Any]) -> List[str]:
    """
    Validate analysis results and return any issues found
    
    Args:
        results: Results to validate
        
    Returns:
        List of validation issues (empty if all good)
    """
    issues = []
    
    # Check required fields
    if 'metadata' not in results:
        issues.append("Missing metadata")
    
    if 'chunk_analyses' not in results:
        issues.append("Missing chunk analyses")
    
    if 'synthesis' not in results:
        issues.append("Missing synthesis")
    
    # Check synthesis quality
    synthesis = results.get('synthesis', {})
    if 'error' in synthesis:
        issues.append(f"Synthesis error: {synthesis['error']}")
    
    # Check for successful chunk processing
    metadata = results.get('metadata', {})
    total_chunks = metadata.get('total_chunks', 0)
    if total_chunks == 0:
        issues.append("No chunks were processed")
    
    successful_chunks = synthesis.get('metadata', {}).get('successful_chunks', 0)
    if successful_chunks == 0:
        issues.append("No chunks were successfully analyzed")
    elif successful_chunks < total_chunks * 0.5:
        issues.append(f"Low success rate: {successful_chunks}/{total_chunks} chunks successful")
    
    return issues

def create_processing_report(results: Dict[str, Any]) -> str:
    """
    Create a processing report
    
    Args:
        results: Analysis results
        
    Returns:
        Processing report as string
    """
    metadata = results.get('metadata', {})
    synthesis_meta = results.get('synthesis', {}).get('metadata', {})
    
    report = f"""
Processing Report
================

Document: {metadata.get('title', 'Unknown')}
Timestamp: {metadata.get('processing_timestamp', 'Unknown')}
Model: {metadata.get('model', 'Unknown')}

Chunking Results:
- Total chunks created: {metadata.get('total_chunks', 0)}
- Total tokens: {metadata.get('total_tokens', 0)}

Analysis Results:
- Successful chunks: {synthesis_meta.get('successful_chunks', 0)}
- Failed chunks: {metadata.get('total_chunks', 0) - synthesis_meta.get('successful_chunks', 0)}

Synthesis:
- Categories processed: {len(synthesis_meta.get('categories_synthesized', []))}
- Synthesis model: {synthesis_meta.get('synthesis_model', 'Unknown')}

Validation:
"""
    
    issues = validate_results(results)
    if issues:
        report += "\nIssues found:\n"
        for issue in issues:
            report += f"- {issue}\n"
    else:
        report += "[OK] All validation checks passed\n"
    
    return report

def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up logging configuration with Unicode support for Windows
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    import sys
    
    # Create handlers with explicit UTF-8 encoding for Windows compatibility
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Force UTF-8 encoding on Windows to handle Unicode characters
    if hasattr(console_handler.stream, 'reconfigure'):
        try:
            console_handler.stream.reconfigure(encoding='utf-8')
        except Exception:
            pass  # If reconfigure fails, continue with default
    
    file_handler = logging.FileHandler('mind_map_creator.log', encoding='utf-8')
    
    # Set up formatters
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=[console_handler, file_handler],
        force=True  # Override any existing configuration
    )

def clean_filename(filename: str) -> str:
    """
    Clean filename to be filesystem-safe
    
    Args:
        filename: Original filename
        
    Returns:
        Cleaned filename
    """
    # Remove or replace problematic characters
    import re
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
    cleaned = re.sub(r'_{2,}', '_', cleaned)  # Replace multiple underscores
    cleaned = cleaned.strip('_.')  # Remove leading/trailing underscores and dots
    
    # Limit length
    if len(cleaned) > 100:
        cleaned = cleaned[:100]
    
    return cleaned or "unnamed"

def save_complete_mindmap_package(results: Dict[str, Any], mindmap_content: str, 
                                notes_content: str, output_dir: Path, 
                                filename_prefix: str = "mindmap") -> Dict[str, Path]:
    """
    Save complete mind map package (mind map + notes + summary)
    
    Args:
        results: Analysis results
        mindmap_content: Mind map content
        notes_content: Explanatory notes content
        output_dir: Directory to save files
        filename_prefix: Prefix for filenames
        
    Returns:
        Dictionary mapping file types to saved paths
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    saved_files = {}
    
    # Save mind map
    mindmap_file = save_mindmap(mindmap_content, output_dir, f"{filename_prefix}.mmd")
    saved_files['mindmap'] = mindmap_file
    
    # Save explanatory notes
    notes_file = save_mindmap_notes(notes_content, output_dir, f"{filename_prefix}_explanation.md")
    saved_files['notes'] = notes_file
    
    # Save quick summary
    metadata = results.get('metadata', {})
    title = metadata.get('title', 'Document Analysis')
    
    summary_content = f"""# {title} - Learning Package

## Files Included

1. **{mindmap_file.name}** - Interactive mind map (open in Mermaid viewer)
2. **{notes_file.name}** - Detailed explanations for students

## How to Use

1. **Start with the mind map**: Open {mindmap_file.name} in a Mermaid-compatible viewer
2. **Read the explanations**: Use {notes_file.name} to understand each concept
3. **Study actively**: Create your own connections between ideas
4. **Apply the knowledge**: Use the actionable insights in real situations

## Quick Access
- **Main Topic**: {title}
- **Generated**: {metadata.get('processing_timestamp', 'Unknown')}
- **AI Model**: {metadata.get('model', 'Unknown')}

*This learning package was created using AI-powered knowledge extraction to help you understand complex ideas quickly and clearly.*
"""
    
    readme_file = output_dir / f"{filename_prefix}_README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    saved_files['readme'] = readme_file
    
    logger.info(f"Complete mind map package saved to {output_dir}")
    logger.info(f"Files: {', '.join([f.name for f in saved_files.values()])}")
    
    return saved_files
