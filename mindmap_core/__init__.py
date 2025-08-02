"""
Mind Map Creator - AI-Powered Knowledge Extraction and Mind Mapping

This package provides tools for extracting insights from text documents
and generating mind maps using advanced AI techniques.
"""

__version__ = "1.0.0"
__author__ = "Mind Map Creator Team"

import logging
from .extractor import KnowledgeExtractor
from .mindmap_generator import MindMapGenerator
from .chunker import SmartTextChunker
from .synthesizer import InsightSynthesizer
from .notes_generator import MindMapNotesGenerator
from .web_config import Config

logger = logging.getLogger(__name__)

# Main class for easy usage
class MindMapCreator:
    """
    Main interface for the Mind Map Creator system
    """
    
    def __init__(self, model: str = None, api_key: str = None, config: Config = None):
        """
        Initialize the Mind Map Creator
        
        Args:
            model: AI model to use (gpt-3.5-turbo or gpt-4)
            api_key: OpenAI API key (optional, will use config/env if not provided)
            config: Configuration object (optional, will create default if not provided)
        """
        self.config = config or Config()
        self.model = model or self.config.DEFAULT_MODEL
        self.api_key = api_key or self.config.OPENAI_API_KEY
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.extractor = KnowledgeExtractor(api_key=self.api_key, model=self.model)
        self.mindmap_generator = MindMapGenerator(self.extractor.client, self.model)
        self.notes_generator = MindMapNotesGenerator(self.extractor.client, self.model)
        
    def process_chapter(self, content: str = None, file_path: str = None, title: str = "") -> dict:
        """
        Process a chapter from content or file
        
        Args:
            content: Text content to process (alternative to file_path)
            file_path: Path to the chapter file (alternative to content)
            title: Title for the chapter
            
        Returns:
            Dictionary containing insights and analysis results
        """
        if content is not None:
            results = self.extractor.extract_insights(content, title)
        elif file_path is not None:
            results = self.extractor.process_file(file_path)
        else:
            raise ValueError("Either content or file_path must be provided")
        
        # Generate student summary using GPT
        try:
            quick_summary = self.create_student_summary(results)
            results['quick_summary'] = quick_summary
        except Exception as e:
            logger.error(f"Error generating student summary: {str(e)}")
            results['quick_summary'] = ""
        
        return results
    
    def create_mindmap(self, results: dict, mindmap_type: str = "comprehensive") -> str:
        """
        Generate mind map from analysis results
        
        Args:
            results: Analysis results dictionary
            mindmap_type: Type of mind map to generate (main, actionable, relationship, comprehensive)
            
        Returns:
            Mermaid format mind map string
        """
        return self.mindmap_generator.generate_mindmap_from_synthesis(results, mindmap_type)
    
    def create_notes(self, results: dict, mindmap_content: str) -> str:
        """
        Generate enhanced explanatory notes with CAPTURE framework integration
        
        Args:
            results: Analysis results dictionary
            mindmap_content: Generated mind map content
            
        Returns:
            Formatted notes as markdown string with comprehensive summaries
        """
        return self.notes_generator.generate_mindmap_notes(results, mindmap_content)
    
    def create_student_summary(self, results: dict) -> str:
        """
        Generate brief summary for students
        
        Args:
            results: Analysis results dictionary
            
        Returns:
            Brief summary text
        """
        return self.notes_generator.generate_student_summary(results)

__all__ = [
    'MindMapCreator',
    'KnowledgeExtractor', 
    'MindMapGenerator',
    'MindMapNotesGenerator',
    'SmartTextChunker',
    'InsightSynthesizer'
]
