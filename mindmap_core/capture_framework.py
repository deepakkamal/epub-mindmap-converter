"""
CAPTURE Framework for Enhanced Comprehension and Summarization
Based on research-backed comprehension strategies including FASCT, SWBST, and text structure analysis
"""

import json
import logging
from typing import Dict, List, Any, Tuple
from .web_config import Config

logger = logging.getLogger(__name__)

class CAPTUREFramework:
    """
    Comprehensive Analysis and Processing Through Understanding, Reasoning, and Explanation
    
    This framework implements evidence-based comprehension strategies:
    - C: Comprehension through text structure analysis
    - A: Analysis of patterns (cause-effect, problem-solution, comparison)
    - P: Partitioning content into logical segments
    - T: Thematic extraction using structured frameworks
    - U: Unified synthesis of concepts and relationships
    - R: Response generation with comprehensive summaries
    - E: Explanation strategies for improved understanding
    """
    
    def __init__(self, openai_client, model: str):
        """
        Initialize CAPTURE framework
        
        Args:
            openai_client: OpenAI client instance
            model: AI model to use
        """
        self.client = openai_client
        self.model = model
        self.config = Config()
        
    def apply_capture_analysis(self, content: str, title: str) -> Dict[str, Any]:
        """
        Apply the complete CAPTURE framework to analyze content
        
        Args:
            content: Text content to analyze
            title: Title for context
            
        Returns:
            Comprehensive analysis results
        """
        logger.info(f"Applying CAPTURE framework to: {title}")
        
        try:
            # C: Comprehension through text structure analysis
            structure_analysis = self._analyze_text_structure(content, title)
            
            # A: Analysis of patterns
            pattern_analysis = self._analyze_patterns(content, title)
            
            # P: Partitioning and chunking insights
            partition_analysis = self._analyze_partitions(content, title)
            
            # T: Thematic extraction
            thematic_analysis = self._extract_themes(content, title)
            
            # U: Unified synthesis
            unified_synthesis = self._create_unified_synthesis({
                'structure': structure_analysis,
                'patterns': pattern_analysis,
                'partitions': partition_analysis,
                'themes': thematic_analysis
            }, title)
            
            # R: Response generation with comprehensive summary
            comprehensive_summary = self._generate_comprehensive_summary(unified_synthesis, title)
            
            # E: Explanation strategies
            explanation_strategies = self._generate_explanation_strategies(unified_synthesis, title)
            
            return {
                'capture_analysis': {
                    'structure_analysis': structure_analysis,
                    'pattern_analysis': pattern_analysis,
                    'partition_analysis': partition_analysis,
                    'thematic_analysis': thematic_analysis,
                    'unified_synthesis': unified_synthesis,
                    'comprehensive_summary': comprehensive_summary,
                    'explanation_strategies': explanation_strategies
                },
                'metadata': {
                    'framework': 'CAPTURE',
                    'model_used': self.model,
                    'analysis_components': 7
                }
            }
            
        except Exception as e:
            logger.error(f"Error in CAPTURE analysis: {str(e)}")
            return {
                'capture_analysis': {
                    'error': str(e),
                    'fallback_summary': self._generate_fallback_summary(content, title)
                }
            }
    
    def _analyze_text_structure(self, content: str, title: str) -> Dict[str, Any]:
        """
        C: Comprehension through text structure analysis (based on FASCT)
        """
        prompt = f"""
        Analyze the text structure of "{title}" to improve comprehension.
        
        Text content:
        {content[:3000]}...
        
        Identify the following text structures present:
        1. Problem-Solution structures
        2. Cause-Effect relationships
        3. Comparison structures
        4. Sequential/Process structures
        5. Description/Definition structures
        
        For each structure found, provide:
        - Type of structure
        - Key elements identified
        - How this structure supports comprehension
        - Main organizing principle
        
        Format as JSON:
        {{
            "primary_structure": "structure_type",
            "secondary_structures": ["type1", "type2"],
            "structure_elements": {{
                "problem_solution": {{"problems": [], "solutions": []}},
                "cause_effect": {{"causes": [], "effects": []}},
                "comparisons": {{"items_compared": [], "comparison_points": []}},
                "sequences": {{"steps": [], "processes": []}},
                "descriptions": {{"main_concepts": [], "key_characteristics": []}}
            }},
            "comprehension_aids": []
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            content_response = response.choices[0].message.content.strip()
            return json.loads(self._clean_json_response(content_response))
            
        except Exception as e:
            logger.error(f"Error in structure analysis: {str(e)}")
            return {"error": str(e), "primary_structure": "mixed"}
    
    def _analyze_patterns(self, content: str, title: str) -> Dict[str, Any]:
        """
        A: Analysis of narrative and informational patterns
        """
        prompt = f"""
        Analyze the content patterns in "{title}" using proven comprehension frameworks.
        
        Text content:
        {content[:3000]}...
        
        Apply the SWBST framework (Somebody Wanted But So Then) if applicable:
        - Somebody: Who are the main actors/subjects?
        - Wanted: What are the goals/objectives?
        - But: What obstacles/problems exist?
        - So: What solutions/actions were taken?
        - Then: What were the outcomes/results?
        
        Also identify:
        - Cause and effect chains
        - Problem-solution sequences
        - Main conflicts and resolutions
        - Key decision points and consequences
        
        Format as JSON:
        {{
            "swbst_analysis": {{
                "somebody": [],
                "wanted": [],
                "but": [],
                "so": [],
                "then": []
            }},
            "cause_effect_chains": [
                {{"cause": "description", "effect": "description", "significance": "why important"}}
            ],
            "problem_solution_pairs": [
                {{"problem": "description", "solution": "description", "effectiveness": "assessment"}}
            ],
            "decision_consequences": [],
            "main_conflicts": []
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            content_response = response.choices[0].message.content.strip()
            return json.loads(self._clean_json_response(content_response))
            
        except Exception as e:
            logger.error(f"Error in pattern analysis: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_partitions(self, content: str, title: str) -> Dict[str, Any]:
        """
        P: Partitioning content into logical segments for better understanding
        """
        prompt = f"""
        Analyze how "{title}" can be partitioned into logical segments for improved comprehension.
        
        Text content:
        {content[:3000]}...
        
        Identify:
        1. Natural break points in the content
        2. Hierarchical structure (main sections, subsections)
        3. Topic boundaries and transitions
        4. Information density patterns
        5. Conceptual groupings
        
        For each partition:
        - Purpose and function
        - Key concepts contained
        - Relationship to other sections
        - Cognitive load assessment
        
        Format as JSON:
        {{
            "logical_partitions": [
                {{
                    "section_id": "intro",
                    "title": "section_title",
                    "purpose": "why this section exists",
                    "key_concepts": [],
                    "relationships": [],
                    "cognitive_load": "low/medium/high"
                }}
            ],
            "hierarchical_structure": {{
                "main_sections": [],
                "subsections": [],
                "depth_levels": 0
            }},
            "transition_points": [],
            "information_flow": "description of how information is organized"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            content_response = response.choices[0].message.content.strip()
            return json.loads(self._clean_json_response(content_response))
            
        except Exception as e:
            logger.error(f"Error in partition analysis: {str(e)}")
            return {"error": str(e)}
    
    def _extract_themes(self, content: str, title: str) -> Dict[str, Any]:
        """
        T: Thematic extraction using structured approaches
        """
        prompt = f"""
        Extract themes from "{title}" using structured comprehension strategies.
        
        Text content:
        {content[:3000]}...
        
        Identify:
        1. Central themes and their supporting evidence
        2. Conceptual relationships between themes
        3. Theme hierarchy (primary, secondary, supporting)
        4. Theme development throughout the text
        5. Practical applications of each theme
        
        For each theme:
        - Clear definition
        - Supporting evidence
        - Connections to other themes
        - Real-world relevance
        - Student comprehension strategies
        
        Format as JSON:
        {{
            "primary_themes": [
                {{
                    "theme": "theme_name",
                    "definition": "clear explanation",
                    "evidence": [],
                    "connections": [],
                    "applications": [],
                    "comprehension_strategy": "how students can understand this"
                }}
            ],
            "secondary_themes": [],
            "theme_relationships": [
                {{"theme1": "name", "theme2": "name", "relationship": "description"}}
            ],
            "theme_progression": "how themes develop through the text",
            "unifying_concept": "overarching idea that ties themes together"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            content_response = response.choices[0].message.content.strip()
            return json.loads(self._clean_json_response(content_response))
            
        except Exception as e:
            logger.error(f"Error in thematic analysis: {str(e)}")
            return {"error": str(e)}
    
    def _create_unified_synthesis(self, analyses: Dict[str, Any], title: str) -> Dict[str, Any]:
        """
        U: Unified synthesis of all analysis components
        """
        prompt = f"""
        Create a unified synthesis for "{title}" by integrating multiple analysis components.
        
        Analysis Components:
        {json.dumps(analyses, indent=2)[:4000]}...
        
        Synthesize into a coherent understanding that includes:
        1. Main message and purpose
        2. Key concepts and their relationships
        3. Logical flow and structure
        4. Critical insights and takeaways
        5. Practical applications
        6. Connection points for student understanding
        
        Focus on creating a synthesis that:
        - Integrates all analytical perspectives
        - Highlights most important elements
        - Shows relationships between concepts
        - Provides clear learning pathways
        - Emphasizes practical value
        
        Format as JSON:
        {{
            "main_message": "overarching purpose and meaning",
            "core_concepts": [
                {{"concept": "name", "definition": "clear explanation", "importance": "why it matters", "connections": []}}
            ],
            "logical_framework": "how the content is organized and flows",
            "critical_insights": [],
            "practical_applications": [],
            "learning_pathways": [],
            "comprehension_barriers": [],
            "success_indicators": "how to know students understand"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            content_response = response.choices[0].message.content.strip()
            return json.loads(self._clean_json_response(content_response))
            
        except Exception as e:
            logger.error(f"Error in unified synthesis: {str(e)}")
            return {"error": str(e)}
    
    def _generate_comprehensive_summary(self, synthesis: Dict[str, Any], title: str) -> str:
        """
        R: Response generation with comprehensive summary
        """
        prompt = f"""
        Generate a comprehensive summary for "{title}" based on the unified synthesis.
        
        Synthesis Data:
        {json.dumps(synthesis, indent=2)[:3000]}...
        
        Create a comprehensive summary that includes:
        
        1. **Executive Overview** (2-3 paragraphs)
           - What this content is about and why it matters
           - Main purpose and audience
           - Key value proposition
        
        2. **Core Concepts & Frameworks** (organized by importance)
           - Essential concepts with clear explanations
           - Mental models and frameworks presented
           - How concepts relate to each other
        
        3. **Key Insights & Discoveries**
           - Most important insights and their implications
           - New perspectives or ways of thinking
           - Critical connections and patterns
        
        4. **Practical Applications**
           - How to apply these concepts in real situations
           - Specific examples and use cases
           - Implementation strategies
        
        5. **Main Takeaways**
           - 5-7 most important points to remember
           - Action items and next steps
           - Success metrics and indicators
        
        Write in clear, accessible language that helps students understand complex ideas.
        Aim for 600-800 words total. Use engaging headings and clear transitions.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating comprehensive summary: {str(e)}")
            return f"# Comprehensive Summary: {title}\n\nError generating detailed summary: {str(e)}"
    
    def _generate_explanation_strategies(self, synthesis: Dict[str, Any], title: str) -> Dict[str, Any]:
        """
        E: Explanation strategies for improved understanding
        """
        prompt = f"""
        Generate explanation strategies for "{title}" to improve student understanding.
        
        Synthesis Data:
        {json.dumps(synthesis, indent=2)[:2000]}...
        
        Create strategies for:
        1. Pre-reading preparation (activating prior knowledge)
        2. During-reading comprehension aids
        3. Post-reading consolidation activities
        4. Memory and retention techniques
        5. Application and transfer strategies
        
        For each strategy:
        - Clear description
        - Step-by-step implementation
        - Expected outcomes
        - Assessment criteria
        
        Format as JSON:
        {{
            "pre_reading": [
                {{"strategy": "name", "description": "how to implement", "purpose": "why it helps"}}
            ],
            "during_reading": [],
            "post_reading": [],
            "memory_techniques": [],
            "application_strategies": [],
            "assessment_approaches": [],
            "differentiation_options": []
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            content_response = response.choices[0].message.content.strip()
            return json.loads(self._clean_json_response(content_response))
            
        except Exception as e:
            logger.error(f"Error generating explanation strategies: {str(e)}")
            return {"error": str(e)}
    
    def _clean_json_response(self, content: str) -> str:
        """Clean JSON response from AI"""
        import re
        
        # Remove markdown code blocks
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*$', '', content)
        content = content.strip()
        
        # Fix common JSON issues
        content = re.sub(r',\s*}', '}', content)  # Remove trailing commas
        content = re.sub(r',\s*]', ']', content)   # Remove trailing commas in arrays
        
        return content
    
    def _generate_fallback_summary(self, content: str, title: str) -> str:
        """Generate fallback summary if main analysis fails"""
        return f"""
        # Comprehensive Summary: {title}
        
        ## Overview
        This content covers important concepts and insights related to {title}.
        
        ## Key Points
        - Analysis of main themes and concepts
        - Identification of practical applications
        - Understanding of relationships between ideas
        
        ## Next Steps
        Review the mind map and detailed notes for deeper understanding.
        """