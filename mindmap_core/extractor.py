"""
Knowledge extraction module for analyzing text chunks
"""

import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Any
import openai
from .web_config import Config
from .chunker import SmartTextChunker
from .capture_framework import CAPTUREFramework

logger = logging.getLogger(__name__)

class KnowledgeExtractor:
    """
    Extracts knowledge and insights from text using AI
    """
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize the knowledge extractor
        
        Args:
            api_key: OpenAI API key
            model: AI model to use
        """
        self.config = Config()
        self.api_key = api_key or self.config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
            
        self.model = model or self.config.DEFAULT_MODEL
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Get model-specific configuration
        model_config = self.config.get_model_config(self.model)
        self.chunker = SmartTextChunker(
            config=self.config,
            max_tokens=model_config['chunk_size'],
            overlap_tokens=self.config.CHUNK_OVERLAP_TOKENS
        )
        
        # Initialize CAPTURE framework for enhanced analysis
        self.capture_framework = CAPTUREFramework(self.client, self.model)
        
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process a single file and extract knowledge
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Dictionary containing extracted insights
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if file_path.suffix not in self.config.SUPPORTED_FILE_TYPES:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        logger.info(f"Processing file: {file_path.name}")
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.extract_insights(content, file_path.stem)
    
    def extract_insights(self, text: str, title: str = "") -> Dict[str, Any]:
        """
        Extract insights from text using chunking approach
        
        Args:
            text: Text to analyze
            title: Title for context
            
        Returns:
            Dictionary containing all extracted insights
        """
        logger.info(f"Starting insight extraction for: {title}")
        
        # Step 1: Apply CAPTURE framework for comprehensive analysis
        capture_analysis = self.capture_framework.apply_capture_analysis(text, title)
        logger.info("Completed CAPTURE framework analysis")
        
        # Step 2: Chunk the text intelligently
        chunks = self.chunker.chunk_by_sections(text, title)
        logger.info(f"Created {len(chunks)} chunks for analysis")
        
        # Step 3: Analyze each chunk
        chunk_analyses = []
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"Analyzing chunk {i}/{len(chunks)} ({chunk['token_estimate']} tokens)")
            
            try:
                analysis = self._analyze_chunk(chunk, title)
                chunk_analyses.append({
                    'chunk_info': chunk,
                    'analysis': analysis
                })
            except Exception as e:
                logger.error(f"Error analyzing chunk {i}: {str(e)}")
                chunk_analyses.append({
                    'chunk_info': chunk,
                    'analysis': {'error': str(e)}
                })
        
        # Step 3: Synthesize insights (will be done by synthesizer module)
        from .synthesizer import InsightSynthesizer
        synthesizer = InsightSynthesizer(self.client, self.model)
        synthesis = synthesizer.synthesize_insights(chunk_analyses, title)
        
        return {
            'metadata': {
                'title': title,
                'model': self.model,
                'total_chunks': len(chunks),
                'total_tokens': sum(c['token_estimate'] for c in chunks),
                'processing_timestamp': self._get_timestamp(),
                'capture_framework_applied': True
            },
            'chunk_analyses': chunk_analyses,
            'synthesis': synthesis,
            'capture_analysis': capture_analysis
        }
    
    def _analyze_chunk(self, chunk: Dict[str, Any], title: str) -> Dict[str, Any]:
        """
        Analyze a single chunk of text using multiple focused question sets
        
        Args:
            chunk: Chunk dictionary with content and metadata
            title: Document title for context
            
        Returns:
            Dictionary containing comprehensive chunk analysis
        """
        logger.info(f"Analyzing chunk with multi-set approach")
        
        # Define question sets (4 questions each for better model performance)
        question_sets = [
            {
                "name": "core_concepts",
                "questions": [
                    "What are the main concepts or ideas presented?",
                    "What key terminology or definitions are introduced?", 
                    "What fundamental principles are explained?",
                    "What core themes emerge from this section?"
                ]
            },
            {
                "name": "evidence_insights",
                "questions": [
                    "What evidence, examples, or data support the main ideas?",
                    "What historical cases or real-world examples are provided?",
                    "What deeper insights or implications can be drawn?",
                    "What patterns or trends are highlighted?"
                ]
            },
            {
                "name": "relationships_applications", 
                "questions": [
                    "How do the concepts relate to each other?",
                    "What cause-and-effect relationships are described?",
                    "How can these ideas be applied practically?",
                    "What connections exist with broader themes?"
                ]
            },
            {
                "name": "critical_thinking",
                "questions": [
                    "What questions is the author trying to answer?",
                    "What problems or challenges are being addressed?",
                    "What contradictions or tensions are present?",
                    "What actionable takeaways can be derived?"
                ]
            }
        ]
        
        # Analyze with each question set
        comprehensive_analysis = {}
        
        for question_set in question_sets:
            try:
                prompt = self._build_focused_prompt(chunk, title, question_set)
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                
                content = response.choices[0].message.content
                content = self._clean_json_response(content)
                
                set_analysis = json.loads(content)
                comprehensive_analysis[question_set["name"]] = set_analysis
                
                logger.info(f"[OK] Completed {question_set['name']} analysis")
                
            except Exception as e:
                logger.warning(f"Error in {question_set['name']} analysis: {str(e)}")
                comprehensive_analysis[question_set["name"]] = {
                    'error': str(e),
                    'fallback': f"Analysis failed for {question_set['name']}"
                }
        
        # Combine results into unified structure
        return self._combine_analysis_sets(comprehensive_analysis)
    
    def _build_analysis_prompt(self, chunk: Dict[str, Any], title: str) -> str:
        """
        Build analysis prompt for a chunk
        
        Args:
            chunk: Chunk to analyze
            title: Document title
            
        Returns:
            Formatted prompt string
        """
        return f"""
        Analyze this section from "{title}".
        
        Section Info: {chunk['section_info']}
        Word Count: {chunk['word_count']} words
        
        Content:
        {chunk['content']}
        
        Extract the following information and format as JSON:
        
        1. "key_concepts": List of main ideas, principles, or frameworks (3-7 items)
        2. "evidence_examples": Stories, data, research, or supporting examples (2-5 items)  
        3. "relationships": How concepts connect to each other (2-5 relationships)
        4. "insights": Important takeaways or implications (3-6 insights)
        5. "questions_raised": Questions this section brings up (1-3 questions)
        
        For each item, provide:
        - Clear, concise description
        - Importance level (1-5 scale)
        - Brief explanation of significance
        
        Focus on actionable and meaningful information. Be thorough but concise.
        """
    
    def _build_focused_prompt(self, chunk: Dict[str, Any], title: str, question_set: Dict[str, Any]) -> str:
        """
        Build focused prompt for a specific question set
        
        Args:
            chunk: Text chunk to analyze
            title: Document title
            question_set: Set of 4 related questions
            
        Returns:
            Formatted prompt string
        """
        text_content = chunk.get('content', '')
        section_info = f"Section {chunk.get('section_number', '?')}"
        
        return f"""
        Document: {title} - {section_info}
        
        Focus Area: {question_set['name'].replace('_', ' ').title()}
        
        Text to analyze:
        {text_content[:4000]}...
        
        Please answer these 4 questions with focused, specific responses:
        
        1. {question_set['questions'][0]}
        2. {question_set['questions'][1]} 
        3. {question_set['questions'][2]}
        4. {question_set['questions'][3]}
        
        Requirements:
        - Provide 2-4 specific points per question
        - Base answers directly on the text content
        - Use clear, concise language
        - Extract actionable insights where possible
        
        Return your response as valid JSON in this format:
        {{
            "question_1": ["point 1", "point 2", "point 3"],
            "question_2": ["point 1", "point 2"],
            "question_3": ["point 1", "point 2", "point 3"],
            "question_4": ["point 1", "point 2"]
        }}
        """
    
    def _clean_json_response(self, content: str) -> str:
        """
        Clean JSON response from AI
        
        Args:
            content: Raw response content
            
        Returns:
            Cleaned JSON string
        """
        # Remove markdown code blocks
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*$', '', content)
        content = content.strip()
        
        # Fix common JSON issues
        content = re.sub(r',\s*}', '}', content)  # Remove trailing commas
        content = re.sub(r',\s*]', ']', content)   # Remove trailing commas in arrays
        
        return content
    
    def _combine_analysis_sets(self, comprehensive_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combine multiple analysis sets into unified structure
        
        Args:
            comprehensive_analysis: Dictionary of analysis sets
            
        Returns:
            Unified analysis structure
        """
        combined = {
            'key_concepts': [],
            'evidence_and_examples': [],
            'relationships': [],
            'insights': [],
            'questions_raised': [],
            'actionable_takeaways': [],
            'analysis_quality': 'multi_set'
        }
        
        # Extract from core_concepts set
        core_concepts = comprehensive_analysis.get('core_concepts', {})
        if 'question_1' in core_concepts:
            combined['key_concepts'].extend(core_concepts.get('question_1', []))
        if 'question_2' in core_concepts:
            combined['key_concepts'].extend(core_concepts.get('question_2', []))
        if 'question_3' in core_concepts:
            combined['key_concepts'].extend(core_concepts.get('question_3', []))
        
        # Extract from evidence_insights set  
        evidence_insights = comprehensive_analysis.get('evidence_insights', {})
        if 'question_1' in evidence_insights:
            combined['evidence_and_examples'].extend(evidence_insights.get('question_1', []))
        if 'question_2' in evidence_insights:
            combined['evidence_and_examples'].extend(evidence_insights.get('question_2', []))
        if 'question_3' in evidence_insights:
            combined['insights'].extend(evidence_insights.get('question_3', []))
        
        # Extract from relationships_applications set
        relationships = comprehensive_analysis.get('relationships_applications', {})
        if 'question_1' in relationships:
            combined['relationships'].extend(relationships.get('question_1', []))
        if 'question_2' in relationships:
            combined['relationships'].extend(relationships.get('question_2', []))
        if 'question_3' in relationships:
            combined['actionable_takeaways'].extend(relationships.get('question_3', []))
        
        # Extract from critical_thinking set
        critical_thinking = comprehensive_analysis.get('critical_thinking', {})
        if 'question_1' in critical_thinking:
            combined['questions_raised'].extend(critical_thinking.get('question_1', []))
        if 'question_4' in critical_thinking:
            combined['actionable_takeaways'].extend(critical_thinking.get('question_4', []))
        
        # Add metadata
        combined['raw_analysis_sets'] = comprehensive_analysis
        combined['processing_approach'] = 'focused_question_sets'
        
        return combined
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def estimate_cost(self, text: str) -> Dict[str, float]:
        """
        Estimate processing cost for text
        
        Args:
            text: Text to estimate cost for
            
        Returns:
            Dictionary with cost estimates
        """
        token_count = self.chunker.estimate_tokens(text)
        model_config = self.config.get_model_config(self.model)
        
        # Estimate total tokens (input + output)
        estimated_total_tokens = token_count * 1.5  # Rough estimate including output
        
        cost = (estimated_total_tokens / 1000) * model_config['cost_per_1k_tokens']
        
        return {
            'estimated_input_tokens': token_count,
            'estimated_total_tokens': estimated_total_tokens,
            'estimated_cost_usd': round(cost, 4),
            'model': self.model
        }
