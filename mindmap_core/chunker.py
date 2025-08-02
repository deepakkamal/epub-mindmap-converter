"""
Smart text chunking module for handling large documents
"""

import re
import logging
from typing import List, Dict, Any
from .web_config import Config

logger = logging.getLogger(__name__)

class SmartTextChunker:
    """
    Intelligently chunks text while preserving context and meaning
    """
    
    def __init__(self, config: Config = None, max_tokens: int = None, overlap_tokens: int = None):
        self.config = config or Config()
        self.max_tokens = max_tokens or self.config.MAX_TOKENS_PER_CHUNK
        self.overlap_tokens = overlap_tokens or self.config.OVERLAP_TOKENS
        
    def estimate_tokens(self, text: str) -> int:
        """
        Rough token estimation (1 token ≈ 4 characters)
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        return len(text) // 4
    
    def chunk_by_sections(self, text: str, title: str = "") -> List[Dict[str, Any]]:
        """
        Chunk text by logical sections while respecting token limits
        
        Args:
            text: Text to chunk
            title: Document title for context
            
        Returns:
            List of chunk dictionaries with metadata
        """
        logger.info(f"Chunking text: {title}")
        
        # First, try to identify natural sections
        sections = self._identify_sections(text)
        logger.info(f"Identified {len(sections)} natural sections")
        
        chunks = []
        current_chunk = ""
        current_tokens = 0
        chunk_number = 1
        
        for section in sections:
            section_tokens = self.estimate_tokens(section['content'])
            
            # If section alone exceeds limit, split it further
            if section_tokens > self.max_tokens:
                # Save current chunk if it has content
                if current_chunk.strip():
                    chunks.append(self._create_chunk_dict(
                        chunk_number, current_chunk, current_tokens, 
                        f"Sections ending with {section['title']}"
                    ))
                    chunk_number += 1
                    current_chunk = ""
                    current_tokens = 0
                
                # Split large section into smaller parts
                sub_chunks = self._split_large_section(section['content'], section['title'])
                for sub_chunk in sub_chunks:
                    chunks.append(self._create_chunk_dict(
                        chunk_number, sub_chunk, self.estimate_tokens(sub_chunk),
                        f"{section['title']} - Part {chunk_number}"
                    ))
                    chunk_number += 1
                    
            else:
                # Check if adding this section would exceed limit
                if current_tokens + section_tokens > self.max_tokens and current_chunk:
                    # Save current chunk
                    chunks.append(self._create_chunk_dict(
                        chunk_number, current_chunk, current_tokens,
                        f"Sections ending before {section['title']}"
                    ))
                    chunk_number += 1
                    
                    # Start new chunk with overlap
                    overlap_text = self._get_overlap_text(current_chunk)
                    current_chunk = overlap_text + "\n\n" + section['content']
                    current_tokens = self.estimate_tokens(current_chunk)
                else:
                    # Add to current chunk
                    if current_chunk:
                        current_chunk += "\n\n" + section['content']
                        current_tokens += section_tokens
                    else:
                        current_chunk = section['content']
                        current_tokens = section_tokens
        
        # Add final chunk if it has content
        if current_chunk.strip():
            chunks.append(self._create_chunk_dict(
                chunk_number, current_chunk, current_tokens, "Final section"
            ))
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
    
    def _create_chunk_dict(self, number: int, content: str, tokens: int, info: str) -> Dict[str, Any]:
        """Create standardized chunk dictionary"""
        return {
            'chunk_number': number,
            'content': content.strip(),
            'token_estimate': tokens,
            'section_info': info,
            'word_count': len(content.split()),
            'character_count': len(content)
        }
    
    def _identify_sections(self, text: str) -> List[Dict[str, str]]:
        """
        Identify logical sections in the text
        
        Args:
            text: Text to analyze
            
        Returns:
            List of section dictionaries
        """
        sections = []
        
        # Split by headers (markdown style)
        header_pattern = r'\n(#{1,6}\s+.*?)\n'
        parts = re.split(header_pattern, text)
        
        if len(parts) == 1:
            # No clear headers, split by paragraphs
            sections = self._split_by_paragraphs(text)
        else:
            # Process parts with headers
            sections = self._process_header_sections(parts)
        
        # Filter out empty sections
        sections = [s for s in sections if s['content'].strip()]
        
        return sections
    
    def _split_by_paragraphs(self, text: str) -> List[Dict[str, str]]:
        """Split text by paragraphs when no headers are found"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        sections = []
        current_section = ""
        section_count = 1
        
        for para in paragraphs:
            if len(current_section) + len(para) > 2000:  # Rough section size
                if current_section:
                    sections.append({
                        'title': f"Section {section_count}",
                        'content': current_section.strip()
                    })
                    section_count += 1
                current_section = para
            else:
                current_section = current_section + "\n\n" + para if current_section else para
        
        if current_section:
            sections.append({
                'title': f"Section {section_count}",
                'content': current_section.strip()
            })
        
        return sections
    
    def _process_header_sections(self, parts: List[str]) -> List[Dict[str, str]]:
        """Process text parts that contain headers"""
        sections = []
        
        for i in range(0, len(parts)):
            if i % 2 == 1:  # This is a header
                header = parts[i].strip()
                # Get content after this header
                content_parts = []
                
                # Add content before header if it exists and is substantial
                if i > 0 and parts[i-1].strip():
                    content_parts.append(parts[i-1].strip())
                
                # Add content after header
                if i + 1 < len(parts):
                    content_parts.append(parts[i+1].strip())
                
                content = "\n\n".join(content_parts)
                
                if content.strip():
                    sections.append({
                        'title': header,
                        'content': content
                    })
        
        # Handle case where first part is content without header
        if len(parts) > 0 and parts[0].strip() and not parts[0].startswith('#'):
            sections.insert(0, {
                'title': "Introduction",
                'content': parts[0].strip()
            })
        
        return sections
    
    def _split_large_section(self, content: str, title: str) -> List[str]:
        """
        Split a large section into smaller chunks
        
        Args:
            content: Content to split
            title: Section title for logging
            
        Returns:
            List of content chunks
        """
        logger.info(f"Splitting large section: {title}")
        
        # Try to split by sentences first
        sentences = re.split(r'(?<=[.!?])\s+', content)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            if self.estimate_tokens(test_chunk) > self.max_tokens:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    # Single sentence is too long, split by words
                    word_chunks = self._split_by_words(sentence)
                    chunks.extend(word_chunks)
            else:
                current_chunk = test_chunk
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _split_by_words(self, text: str) -> List[str]:
        """Split text by words when sentences are too long"""
        words = text.split()
        chunks = []
        current_chunk = ""
        
        for word in words:
            test_chunk = current_chunk + " " + word if current_chunk else word
            
            if self.estimate_tokens(test_chunk) > self.max_tokens:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = word
            else:
                current_chunk = test_chunk
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _get_overlap_text(self, text: str) -> str:
        """
        Get the last part of text for overlap between chunks
        
        Args:
            text: Source text
            
        Returns:
            Overlap text
        """
        target_length = self.overlap_tokens * 4  # Rough character equivalent
        
        if len(text) <= target_length:
            return text
        
        # Find a good breaking point (sentence boundary)
        overlap_start = len(text) - target_length
        overlap_text = text[overlap_start:]
        
        # Try to start at a sentence boundary
        sentences = re.split(r'(?<=[.!?])\s+', overlap_text)
        
        if len(sentences) > 1:
            return " ".join(sentences[1:])  # Skip partial first sentence
        else:
            return overlap_text
