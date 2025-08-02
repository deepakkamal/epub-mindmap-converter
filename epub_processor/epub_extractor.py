#!/usr/bin/env python3
"""
Universal EPUB to Markdown Converter

This script converts EPUB files into filtered markdown files, extracting only meaningful
content chapters while skipping navigation, metadata, and empty sections.

Features:
- Automatic content type detection (chapters, introduction, appendix, etc.)
- Configurable minimum content length filtering
- Optional inclusion of back matter (glossary, about author, etc.)
- Works with any EPUB book, not specific to particular formatting

Usage:
    python epub_to_markdown.py book.epub
    python epub_to_markdown.py book.epub --output-dir chapters --min-length 1000
    python epub_to_markdown.py --interactive
"""

import os
import re
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple, Any
from xml.dom import minidom
import io
import warnings
import html

# Suppress warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Try to import beautifulsoup4 for HTML parsing, fallback to basic parsing if not available
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    # Note: Using basic HTML parsing when beautifulsoup4 is not available


class EpubChapterExtractor:
    """Extract individual chapters from an EPUB file."""
    
    def __init__(self, epub_data: bytes = None, epub_path: str = None, min_content_length: int = 500, include_back_matter: bool = False):
        """
        Initialize with EPUB file data or path.
        
        Args:
            epub_data: EPUB file content as bytes (for in-memory processing)
            epub_path: Path to the EPUB file (for file-based processing) 
            min_content_length: Minimum character count for a chapter to be included
            include_back_matter: Whether to include glossary, about author, etc.
        """
        if epub_data is not None:
            self.epub_data = epub_data
            self.epub_path = None
            self.is_memory_based = True
        elif epub_path is not None:
            self.epub_path = epub_path
            self.epub_data = None
            self.is_memory_based = False
        else:
            raise ValueError("Either epub_data or epub_path must be provided")
            
        self.min_content_length = min_content_length
        self.include_back_matter = include_back_matter
        
    def extract_toc_structure(self) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Extract the table of contents structure from the EPUB file.
        Returns a list of dictionaries with chapter information and the book metadata.
        """
        chapters = []
        metadata = {}
        
        try:
            # Create ZipFile object from either memory or file
            if self.is_memory_based:
                import io
                zip_data = io.BytesIO(self.epub_data)
                z = zipfile.ZipFile(zip_data, "r")
            else:
                z = zipfile.ZipFile(self.epub_path, "r")
            
            with z:
                # Locate content.opf
                container_dom = minidom.parse(z.open("META-INF/container.xml"))
                opf_path = container_dom.getElementsByTagName("rootfile")[0].getAttribute(
                    "full-path"
                )
                
                # Parse content.opf
                opf_dom = minidom.parse(z.open(opf_path))
                
                # Extract metadata
                metadata = {
                    "title": self._get_text_from_node(opf_dom, "dc:title"),
                    "authors": self._get_all_texts_from_nodes(opf_dom, "dc:creator"),
                    "language": self._get_text_from_node(opf_dom, "dc:language"),
                    "publisher": self._get_text_from_node(opf_dom, "dc:publisher"),
                    "date": self._get_text_from_node(opf_dom, "dc:date"),
                    "description": self._get_text_from_node(opf_dom, "dc:description"),
                    "identifier": self._get_text_from_node(opf_dom, "dc:identifier"),
                }
                
                # Extract manifest items (ID → href mapping)
                manifest = {
                    item.getAttribute("id"): item.getAttribute("href")
                    for item in opf_dom.getElementsByTagName("item")
                }
                
                # Extract spine order (ID refs)
                spine_items = opf_dom.getElementsByTagName("itemref")
                spine_order = [item.getAttribute("idref") for item in spine_items]
                
                # Convert spine order to actual file paths
                base_path = "/".join(
                    opf_path.split("/")[:-1]
                )  # Get base directory of content.opf
                spine = [
                    f"{base_path}/{manifest[item_id]}" if base_path else manifest[item_id]
                    for item_id in spine_order
                    if item_id in manifest
                ]
                
                # Look for NCX file (table of contents)
                ncx_files = [f for f in manifest.values() if f.endswith(".ncx")]
                if ncx_files:
                    ncx_path = f"{base_path}/{ncx_files[0]}" if base_path else ncx_files[0]
                    if ncx_path in z.namelist():
                        ncx_dom = minidom.parse(z.open(ncx_path))
                        nav_points = ncx_dom.getElementsByTagName("navPoint")
                        
                        # Process navigation points to extract chapter structure
                        for nav_point in nav_points:
                            label = self._get_text_from_node(nav_point, "text")
                            content_nodes = nav_point.getElementsByTagName("content")
                            if content_nodes:
                                content = content_nodes[0].getAttribute("src")
                                
                                # Determine chapter type
                                chapter_type = self._determine_chapter_type(label)
                                
                                # Create full path to content
                                if "/" in ncx_path:
                                    content_dir = os.path.dirname(ncx_path)
                                    content_path = f"{content_dir}/{content}"
                                else:
                                    content_path = content
                                
                                # Clean up path (remove relative path components)
                                content_path = self._clean_path(content_path)
                                
                                chapters.append({
                                    "title": label,
                                    "path": content_path,
                                    "type": chapter_type,
                                    "id": nav_point.getAttribute("id")
                                })
                
                # If no NCX file or no chapters extracted, fallback to spine order
                if not chapters:
                    # No TOC structure found. Using spine order as chapters.
                    for i, path in enumerate(spine):
                        chapter_type = "chapter"
                        title = f"Chapter {i+1}"
                        chapters.append({
                            "title": title,
                            "path": path,
                            "type": chapter_type,
                            "id": f"auto_chapter_{i}"
                        })
        except Exception as e:
            # Error extracting TOC structure, using fallback
            pass
            
        return chapters, metadata
    
    def _should_include_chapter(self, chapter_type: str, title: str, content: str) -> bool:
        """
        Determine if a chapter should be included based on its type and content.
        
        Args:
            chapter_type: The determined chapter type
            title: The chapter title
            content: The converted markdown content
            
        Returns:
            True if the chapter should be included, False otherwise
        """
        # Always include these types if they meet minimum content requirements
        core_content_types = {"chapter", "introduction", "preface", "foreword", "appendix", "epilogue"}
        
        # Never include these types (typically navigation/metadata)
        exclude_types = {"toc", "cover", "title_page", "copyright"}
        
        # Include based on content length and user preference
        optional_types = {"acknowledgement", "dedication", "reference", "bibliography", "glossary", "about_author", "index"}
        
        # Structural dividers - usually very short
        structural_types = {"part_divider", "section_divider"}
        
        content_length = len(content.strip())
        
        if chapter_type in exclude_types:
            return False
        elif chapter_type in core_content_types:
            # Core content must meet minimum length to avoid empty chapters
            return content_length >= self.min_content_length
        elif chapter_type in optional_types:
            # Optional content: include if user wants it AND it has substantial content
            return self.include_back_matter and content_length >= self.min_content_length
        elif chapter_type in structural_types:
            # Skip structural dividers (they're usually just headers)
            return False
        else:
            # Unknown type: include if it has substantial content
            return content_length >= self.min_content_length

    def _determine_chapter_type(self, title: str) -> str:
        """
        Determine the type of chapter based on its title using general patterns.
        This works for most books regardless of specific formatting.
        """
        title_lower = title.lower().strip()
        
        # Remove common prefixes/suffixes that might interfere with detection
        title_clean = re.sub(r'^(chapter|ch\.?)\s*\d+\s*[:\-\.]?\s*', '', title_lower)
        title_clean = re.sub(r'^\d+\.\s*', '', title_clean)  # Remove "1. " style numbering
        
        # Core content types
        if re.search(r'\bchapter\s+\d+', title_lower) or re.search(r'^ch\.?\s*\d+', title_lower):
            return "chapter"
        elif any(word in title_clean for word in ["introduction", "intro"]):
            return "introduction"
        elif any(word in title_clean for word in ["preface", "foreword", "prologue"]):
            return "preface"
        elif any(word in title_clean for word in ["epilogue", "afterword", "conclusion"]):
            return "epilogue"
        elif any(word in title_clean for word in ["appendix", "addendum"]):
            return "appendix"
        
        # Front/back matter
        elif any(word in title_clean for word in ["acknowledgment", "acknowledgement", "thanks"]):
            return "acknowledgement"
        elif any(word in title_clean for word in ["dedication", "dedicated to"]):
            return "dedication"
        elif any(word in title_clean for word in ["about the author", "about author", "author bio", "biography"]):
            return "about_author"
        elif any(word in title_clean for word in ["glossary", "definitions", "terminology"]):
            return "glossary"
        elif any(word in title_clean for word in ["bibliography", "references", "sources", "further reading"]):
            return "reference"
        elif any(word in title_clean for word in ["index"]):
            return "index"
        
        # Navigation/metadata
        elif any(word in title_clean for word in ["contents", "table of contents", "toc"]):
            return "toc"
        elif any(word in title_clean for word in ["cover", "front cover", "back cover"]):
            return "cover"
        elif any(word in title_clean for word in ["title page", "half title", "title"]) and len(title_clean) < 20:
            return "title_page"
        elif any(word in title_clean for word in ["copyright", "publication", "isbn", "legal"]):
            return "copyright"
        
        # Structural elements (usually short dividers)
        elif re.search(r'part\s+[ivx\d]+', title_lower) or re.search(r'section\s+\d+', title_lower):
            return "part_divider"
        elif title_clean in ["part one", "part two", "part three", "part four", "part five"]:
            return "part_divider"
        elif len(title_clean) < 15 and any(word in title_clean for word in ["part", "section", "book"]):
            return "section_divider"
        
        # If it contains "chapter" anywhere, it's probably a chapter
        elif "chapter" in title_lower:
            return "chapter"
        
        # Default: if we can't classify it and it's substantial, treat as chapter
        return "chapter"
    
    def _clean_path(self, path: str) -> str:
        """Clean up relative path components."""
        parts = path.split('/')
        result = []
        for part in parts:
            if part == '..':
                if result:
                    result.pop()
            elif part != '.':
                result.append(part)
        return '/'.join(result)
    
    def _get_text_from_node(self, dom, tag_name):
        """Extract text from the first matching node."""
        elements = dom.getElementsByTagName(tag_name)
        if elements and elements[0].firstChild:
            return elements[0].firstChild.nodeValue.strip()
        return ""
    
    def _get_all_texts_from_nodes(self, dom, tag_name):
        """Extract text from all matching nodes as a list."""
        return [
            element.firstChild.nodeValue.strip()
            for element in dom.getElementsByTagName(tag_name)
            if element.firstChild
        ]
    
    def convert_chapter(self, chapter_path: str, z: zipfile.ZipFile) -> str:
        """
        Convert a single chapter to markdown using HTML parsing.
        """
        if chapter_path in z.namelist():
            try:
                with z.open(chapter_path) as f:
                    content = f.read().decode('utf-8', errors='ignore')
                    
                    # Convert HTML to Markdown
                    markdown_content = self._html_to_markdown(content)
                    return markdown_content.strip()
                    
            except Exception as e:
                                    pass  # Handle errors silently
        return ""
    
    def extract_content_from_href(self, href: str) -> str:
        """
        Extract content from a specific href/path in the EPUB.
        """
        try:
            if self.is_memory_based:
                import io
                zip_data = io.BytesIO(self.epub_data)
                z = zipfile.ZipFile(zip_data, "r")
            else:
                z = zipfile.ZipFile(self.epub_path, "r")
            
            with z:
                return self.convert_chapter(href, z)
                
        except Exception as e:
            pass  # Handle errors silently
            return ""

    def _html_to_markdown(self, html_content: str) -> str:
        """
        Convert HTML content to Markdown.
        Uses basic regex parsing which works reliably for EPUB content.
        """
        # For now, just use the basic parsing since it works well
        # BeautifulSoup4 implementation had issues with content extraction
        return self._html_to_markdown_basic(html_content)
    
    def _html_to_markdown_bs4(self, html_content: str) -> str:
        """Convert HTML to Markdown using BeautifulSoup."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()
        
        # Get the main content text with basic formatting
        # Try to find the main content area
        main_content = soup.find('body') or soup.find('div') or soup
        
        # Process text content while preserving structure
        markdown_lines = []
        
        # Process each top-level element in order
        for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'blockquote', 'ul', 'ol', 'li'], recursive=False):
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                level = int(element.name[1])
                text = element.get_text().strip()
                if text:
                    markdown_lines.append('#' * level + ' ' + text)
                    markdown_lines.append('')
            elif element.name == 'p':
                text = element.get_text().strip()
                if text:
                    markdown_lines.append(text)
                    markdown_lines.append('')
            elif element.name == 'blockquote':
                text = element.get_text().strip()
                if text:
                    for line in text.split('\n'):
                        if line.strip():
                            markdown_lines.append(f"> {line.strip()}")
                    markdown_lines.append('')
            elif element.name == 'div':
                # For div elements, get all text recursively
                text = element.get_text().strip()
                if text and len(text) > 20:  # Only include substantial div content
                    # Split into paragraphs on double newlines or significant breaks
                    paragraphs = re.split(r'\n\s*\n', text)
                    for para in paragraphs:
                        para = para.strip()
                        if para:
                            markdown_lines.append(para)
                            markdown_lines.append('')
        
        # If we didn't get much content from structured parsing, fall back to raw text
        if len('\n'.join(markdown_lines).strip()) < 200:
            # Fallback: get all text content
            all_text = main_content.get_text()
            if all_text:
                # Clean up the text
                lines = all_text.split('\n')
                markdown_lines = []
                current_paragraph = []
                
                for line in lines:
                    line = line.strip()
                    if line:
                        current_paragraph.append(line)
                    else:
                        if current_paragraph:
                            markdown_lines.append(' '.join(current_paragraph))
                            markdown_lines.append('')
                            current_paragraph = []
                
                # Add final paragraph if exists
                if current_paragraph:
                    markdown_lines.append(' '.join(current_paragraph))
        
        return '\n'.join(markdown_lines)
    
    def _html_to_markdown_basic(self, html_content: str) -> str:
        """Convert HTML to Markdown using basic regex parsing."""
        # Remove script and style elements
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Convert headers
        html_content = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<h5[^>]*>(.*?)</h5>', r'##### \1', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<h6[^>]*>(.*?)</h6>', r'###### \1', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Convert bold and italic
        html_content = re.sub(r'<(?:strong|b)[^>]*>(.*?)</(?:strong|b)>', r'**\1**', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<(?:em|i)[^>]*>(.*?)</(?:em|i)>', r'*\1*', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Convert paragraphs
        html_content = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Convert line breaks
        html_content = re.sub(r'<br[^>]*/?>', '\n', html_content, flags=re.IGNORECASE)
        
        # Convert blockquotes
        html_content = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', 
                             lambda m: '\n'.join([f'> {line.strip()}' for line in m.group(1).split('\n') if line.strip()]) + '\n\n',
                             html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove remaining HTML tags
        html_content = re.sub(r'<[^>]+>', '', html_content)
        
        # Decode HTML entities
        html_content = html.unescape(html_content)
        
        # Clean up whitespace
        lines = html_content.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
            elif cleaned_lines and cleaned_lines[-1]:  # Add blank lines between content
                cleaned_lines.append('')
        
        return '\n'.join(cleaned_lines)
    
    def convert_epub_to_markdown_files(self, output_dir: str) -> None:
        """Convert EPUB to individual markdown files for each chapter."""
        # Extract TOC structure
        toc_structure = self.extract_toc_structure()
        
        chapters = []
        metadata = {"title": "Unknown", "authors": []}
        processed_chapters = 0
        skipped_chapters = 0
        included_types = set()
        skipped_types = set()
        
        # Process each item
        for item in toc_structure:
            title = item['title']
            chapter_type = item['type']
            href = item['href']
            
            # Extract content and check length
            try:
                content = self.extract_content_from_href(href)
                content_length = len(content.strip()) if content else 0
                
                # Apply content length filter and type filtering
                if (content_length >= self.min_content_length and 
                    chapter_type not in ['cover', 'title_page', 'dedication', 'part_divider'] and
                    (self.include_back_matter or chapter_type not in ['about_author', 'glossary', 'copyright'])):
                    
                    # Create safe filename using processed chapter count for consistent numbering
                    safe_filename = self._create_safe_filename(title, processed_chapters, chapter_type)
                    output_file = os.path.join(output_dir, safe_filename)
                    
                    # Write chapter content to file
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(f"# {title}\n\n{content}")
                    
                    processed_chapters += 1
                    included_types.add(chapter_type)
                else:
                    skipped_chapters += 1
                    skipped_types.add(chapter_type)
            except Exception as e:
                skipped_chapters += 1
                skipped_types.add(chapter_type)
        
        # Create a comprehensive summary file
        summary_content = self._create_processing_summary(
            metadata, processed_chapters, skipped_chapters, 
            len(toc_structure), included_types, skipped_types
        )
        
        summary_file = os.path.join(output_dir, "00_processing_summary.md")
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary_content)
        
        print(f"\n📊 Processing Complete:")
        print(f"   ✓ {processed_chapters} chapters processed")
        print(f"   ✗ {skipped_chapters} items skipped")
        print(f"   📄 Summary saved to: {summary_file}")
        
        if processed_chapters > 0:
            print(f"   📚 Included types: {', '.join(sorted(included_types))}")
            if skipped_types:
                print(f"   🚫 Skipped types: {', '.join(sorted(skipped_types))}")

    def extract_chapters_to_memory(self) -> List[Dict[str, str]]:
        """
        Extract chapters directly to memory without creating files.
        
        Returns:
            List of dictionaries with chapter data:
            [
                {
                    'canonical_name': '05_introduction_introduction',
                    'title': 'Introduction',
                    'content': 'markdown content...',
                    'type': 'introduction'
                },
                ...
            ]
        """
        try:
            # Extract TOC structure
            toc_result = self.extract_toc_structure()
            # extract_toc_structure returns (chapters_list, metadata)
            if isinstance(toc_result, tuple) and len(toc_result) == 2:
                toc_structure, metadata = toc_result
            else:
                # Fallback for unexpected format
                toc_structure = toc_result
                metadata = {}
            
            chapters_data = []
            
            # Process each item
            for i, item in enumerate(toc_structure):
                
                title = item['title']
                content_type = item['type']
                href = item.get('href', item.get('path', ''))  # Use 'path' if 'href' doesn't exist
                
                # Extract content and check length
                try:
                    content = self.extract_content_from_href(href)
                    content_length = len(content.strip()) if content else 0
                    
                    # Apply content length filter
                    if content_length < self.min_content_length:
                        if content_type not in ['cover', 'title_page', 'dedication', 'part_divider', 'about_author', 'glossary', 'copyright']:
                            print(f"  ✗ {content_type}: {title} ({content_length} chars)")
                        continue
                    
                    # Skip certain content types
                    if content_type in ['cover', 'title_page', 'dedication', 'part_divider', 'about_author', 'glossary', 'copyright']:
                        print(f"  ✗ {content_type}: {title} ({content_length} chars)")
                        continue
                    
                    # Include this chapter
                    print(f"  ✓ {content_type}: {title} ({content_length:,} chars)")
                    
                    # Generate canonical name
                    canonical_name = self._generate_canonical_name(title, content_type, len(chapters_data))
                    
                    chapters_data.append({
                        'canonical_name': canonical_name,
                        'title': title,
                        'content': content,
                        'type': content_type,
                        'length': content_length
                    })
                    
                except Exception as e:
                    print(f"  ✗ Error processing {title}: {e}")
                    continue
            
            print(f"\n📊 Processing Complete:")
            print(f"   ✓ {len(chapters_data)} chapters processed")
            print(f"   ✗ {len(toc_structure) - len(chapters_data)} items skipped")
            
            if chapters_data:
                included_types = set(chapter['type'] for chapter in chapters_data)
                excluded_types = set(item['type'] for item in toc_structure if item['type'] not in included_types)
                print(f"   📚 Included types: {', '.join(sorted(included_types))}")
                if excluded_types:
                    print(f"   🚫 Skipped types: {', '.join(sorted(excluded_types))}")
            
            return chapters_data
            
        except Exception as e:
            print(f"ERROR in extract_chapters_to_memory: {e}")
            import traceback
            traceback.print_exc()
            raise
            included_types = set(chapter['type'] for chapter in chapters_data)
            excluded_types = set(item['type'] for item in toc_structure if item['type'] not in included_types)
            print(f"   📚 Included types: {', '.join(sorted(included_types))}")
            if excluded_types:
                print(f"   🚫 Skipped types: {', '.join(sorted(excluded_types))}")
        
        return chapters_data
        """
        Convert the EPUB file to separate markdown files, filtering out empty/non-content chapters.
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract chapters and metadata
        chapters, metadata = self.extract_toc_structure()
        
        # Counters for reporting
        processed_chapters = 0
        skipped_chapters = 0
        included_types = set()
        skipped_types = set()
        
        # Process items
        
        # Process each chapter with filtering
        # Create ZipFile object from either memory or file
        if self.is_memory_based:
            import io
            zip_data = io.BytesIO(self.epub_data)
            z = zipfile.ZipFile(zip_data, "r")
        else:
            z = zipfile.ZipFile(self.epub_path, "r")
            
        with z:
            for i, chapter in enumerate(chapters):
                title = chapter["title"]
                path = chapter["path"]
                chapter_type = chapter["type"]
                
                # Convert chapter content first to determine if it should be included
                markdown_content = self.convert_chapter(path, z)
                content_length = len(markdown_content.strip())
                
                # Check if this chapter should be included
                if self._should_include_chapter(chapter_type, title, markdown_content):
                    # Create safe filename using processed chapter count for consistent numbering
                    safe_filename = self._create_safe_filename(title, processed_chapters, chapter_type)
                    output_file = os.path.join(output_dir, safe_filename)
                    
                    # Write chapter content to file
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(f"# {title}\n\n{markdown_content}")
                    
                    print(f"  ✓ {chapter_type}: {title} ({content_length:,} chars)")
                    processed_chapters += 1
                    included_types.add(chapter_type)
                else:
                    print(f"  ✗ {chapter_type}: {title} ({content_length} chars)")
                    skipped_chapters += 1
                    skipped_types.add(chapter_type)
        
        # Create a comprehensive summary file
        summary_content = self._create_processing_summary(
            metadata, processed_chapters, skipped_chapters, 
            len(chapters), included_types, skipped_types
        )
        
        summary_file = os.path.join(output_dir, "00_processing_summary.md")
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary_content)
        
        # Processing complete (verbose output removed for cleaner terminal)
    
    def _create_processing_summary(self, metadata: dict, processed: int, skipped: int, 
                                 total: int, included_types: set, skipped_types: set) -> str:
        """Create a comprehensive processing summary."""
        summary_lines = []
        summary_lines.append("# EPUB Processing Summary")
        summary_lines.append("")
        
        # Add metadata
        summary_lines.append("## Book Information")
        for key, value in metadata.items():
            if isinstance(value, list):
                value = ", ".join(value)
            if value:
                summary_lines.append(f"- **{key.capitalize()}:** {value}")
        
        # Add processing configuration
        summary_lines.append("\n## Processing Configuration")
        summary_lines.append(f"- **Minimum content length:** {self.min_content_length} characters")
        summary_lines.append(f"- **Include back matter:** {'Yes' if self.include_back_matter else 'No'}")
        
        # Add results
        summary_lines.append("\n## Processing Results")
        summary_lines.append(f"- **Total items found:** {total}")
        summary_lines.append(f"- **Chapters processed:** {processed}")
        summary_lines.append(f"- **Items skipped:** {skipped}")
        summary_lines.append(f"- **Success rate:** {(processed/total*100):.1f}%")
        
        if included_types:
            summary_lines.append(f"\n### Included Content Types")
            for content_type in sorted(included_types):
                summary_lines.append(f"- {content_type}")
        
        if skipped_types:
            summary_lines.append(f"\n### Skipped Content Types")
            for content_type in sorted(skipped_types):
                summary_lines.append(f"- {content_type}")
        
        summary_lines.append(f"\n---")
        summary_lines.append(f"*Generated by EPUB to Markdown Converter*")
        
        return "\n".join(summary_lines)
    
    def _generate_canonical_name(self, title: str, chapter_type: str, index: int) -> str:
        """Generate canonical name for memory-based chapters."""
        # Replace unsafe characters and limit length
        safe_title = re.sub(r'[^\w\s-]', '', title).strip().lower()
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        
        # Add padding to index for correct sorting
        padded_index = str(index + 4).zfill(2)  # Start from 04 to match existing naming
        
        # Create canonical name with index, type and title
        return f"{padded_index}_{chapter_type}_{safe_title[:50]}"

    def _create_safe_filename(self, title: str, index: int, chapter_type: str) -> str:
        """Create a safe filename from chapter title."""
        # Replace unsafe characters and limit length
        safe_title = re.sub(r'[^\w\s-]', '', title).strip().lower()
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        
        # Add padding to index for correct sorting
        padded_index = str(index + 1).zfill(2)
        
        # Create filename with index, type and title
        return f"{padded_index}_{chapter_type}_{safe_title[:50]}.md"
