"""
Insight synthesis module for combining chunk analyses
"""

import json
import logging
from typing import Dict, List, Any
from .web_config import Config

logger = logging.getLogger(__name__)

class InsightSynthesizer:
    """
    Synthesizes insights from multiple chunk analyses
    """
    
    def __init__(self, openai_client, model: str):
        """
        Initialize synthesizer
        
        Args:
            openai_client: OpenAI client instance
            model: AI model to use
        """
        self.client = openai_client
        self.model = model
        
    def synthesize_insights(self, chunk_analyses: List[Dict], title: str) -> Dict[str, Any]:
        """
        Synthesize insights from multiple chunk analyses
        
        Args:
            chunk_analyses: List of chunk analysis results
            title: Document title
            
        Returns:
            Synthesized insights dictionary
        """
        logger.info(f"Synthesizing insights from {len(chunk_analyses)} chunks")
        
        # Collect insights from successful chunk analyses
        collected_data = self._collect_insights(chunk_analyses)
        
        if not collected_data['has_valid_data']:
            logger.warning("No valid data found in chunk analyses")
            return {
                'error': 'No valid insights found',
                'chunk_count': len(chunk_analyses),
                'successful_chunks': 0
            }
        
        # Generate synthesis using AI
        synthesis = self._generate_synthesis(collected_data, title)
        
        # Add metadata
        synthesis['metadata'] = {
            'total_chunks_processed': len(chunk_analyses),
            'successful_chunks': collected_data['successful_chunks'],
            'synthesis_model': self.model,
            'categories_synthesized': list(Config.ANALYSIS_CATEGORIES)
        }
        
        return synthesis
    
    def _collect_insights(self, chunk_analyses: List[Dict]) -> Dict[str, Any]:
        """
        Collect and organize insights from chunk analyses
        
        Args:
            chunk_analyses: List of chunk analysis results
            
        Returns:
            Organized insights data
        """
        collected = {
            'key_concepts': [],
            'evidence_examples': [],
            'relationships': [],
            'insights': [],
            'questions_raised': [],
            'successful_chunks': 0,
            'has_valid_data': False
        }
        
        for chunk_data in chunk_analyses:
            analysis = chunk_data.get('analysis', {})
            
            # Skip chunks with errors
            if 'error' in analysis:
                continue
                
            collected['successful_chunks'] += 1
            
            # Collect data from each category
            for category in ['key_concepts', 'evidence_examples', 'relationships', 'insights', 'questions_raised']:
                if category in analysis and isinstance(analysis[category], list):
                    collected[category].extend(analysis[category])
                    collected['has_valid_data'] = True
        
        # Limit data to prevent token overflow
        for category in collected:
            if isinstance(collected[category], list) and len(collected[category]) > 20:
                collected[category] = collected[category][:20]
        
        return collected
    
    def _generate_synthesis(self, collected_data: Dict[str, Any], title: str) -> Dict[str, Any]:
        """
        Generate synthesis using AI
        
        Args:
            collected_data: Collected insights from chunks
            title: Document title
            
        Returns:
            AI-generated synthesis
        """
        prompt = self._build_synthesis_prompt(collected_data, title)
        
        try:
            logger.info(f"Attempting synthesis with model: {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            logger.info(f"Received response from {self.model}, length: {len(content) if content else 0}")
            
            content = self._clean_json_response(content)
            
            parsed_result = json.loads(content)
            logger.info(f"Successfully parsed JSON response from {self.model}")
            return parsed_result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in synthesis with {self.model}: {str(e)}")
            logger.error(f"Raw response content: {content[:500] if 'content' in locals() else 'No content received'}")
            return self._create_fallback_synthesis(collected_data)
        except Exception as e:
            logger.error(f"Error generating synthesis with {self.model}: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            
            # Try fallback to gpt-4 if o3/newer models fail
            if self.model in ['o3', 'o3-2025-04-16', 'gpt-4.1', 'gpt-4.1-2025-04-14']:
                logger.info(f"Attempting fallback to gpt-4 due to {self.model} failure")
                try:
                    fallback_response = self.client.chat.completions.create(
                        model='gpt-4',
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.3
                    )
                    
                    fallback_content = fallback_response.choices[0].message.content
                    fallback_content = self._clean_json_response(fallback_content)
                    
                    logger.info("Successfully generated synthesis using gpt-4 fallback")
                    return json.loads(fallback_content)
                    
                except Exception as fallback_error:
                    logger.error(f"Fallback to gpt-4 also failed: {str(fallback_error)}")
            
            return self._create_fallback_synthesis(collected_data)
    
    def _build_synthesis_prompt(self, collected_data: Dict[str, Any], title: str) -> str:
        """
        Build synthesis prompt
        
        Args:
            collected_data: Collected insights
            title: Document title
            
        Returns:
            Formatted prompt
        """
        # Prepare data summary for prompt
        data_summary = {
            'key_concepts': collected_data['key_concepts'][:15],
            'evidence_examples': collected_data['evidence_examples'][:10], 
            'relationships': collected_data['relationships'][:10],
            'insights': collected_data['insights'][:15]
        }
        
        return f"""
        Synthesize the following extracted information from "{title}" into a comprehensive analysis.
        
        Extracted Data:
        {json.dumps(data_summary, indent=2)}
        
        Create a synthesis with the following structure (format as JSON):
        
        1. "main_themes": 3-5 overarching themes that run through the document
        2. "key_principles": 5-7 most important principles or rules identified
        3. "critical_insights": 5-7 most valuable and actionable insights
        4. "actionable_takeaways": 5-7 specific actions readers should take
        5. "mental_models": 3-5 ways of thinking or frameworks promoted
        6. "concept_connections": How the main concepts relate to each other
        
        For each category, provide items with:
        - Clear, concise description
        - Importance/priority level (1-5)
        - Brief rationale for inclusion
        
        Focus on:
        - Most significant and universally applicable insights
        - Practical value for readers
        - Clear connections between ideas
        - Actionable recommendations
        
        Avoid:
        - Repetition of similar points
        - Overly granular details
        - Concepts that apply only to narrow contexts
        """
    
    def _clean_json_response(self, content: str) -> str:
        """Clean JSON response"""
        import re
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*$', '', content)
        content = content.strip()
        return content
    
    def _create_fallback_synthesis(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create fallback synthesis when AI generation fails
        
        Args:
            collected_data: Collected insights
            
        Returns:
            Basic synthesis structure
        """
        logger.info("Creating fallback synthesis")
        
        # Extract available data safely
        key_concepts = collected_data.get('key_concepts', [])
        insights = collected_data.get('insights', [])
        relationships = collected_data.get('relationships', [])
        evidence = collected_data.get('evidence_examples', [])
        
        # Create basic synthesis from available data
        synthesis = {
            'main_themes': self._extract_themes(key_concepts + insights),
            'key_principles': self._extract_principles(key_concepts + evidence),
            'critical_insights': insights[:7] if insights else ["Analysis data not available"],
            'actionable_takeaways': self._extract_actionable(insights + key_concepts),
            'mental_models': self._extract_mental_models(key_concepts),
            'concept_connections': relationships[:6] if relationships else [],
            'fallback_mode': True,
            'note': 'Generated using fallback synthesis due to AI processing error'
        }
        
        # If all lists are empty, create a minimal useful response
        if all(not v for v in [key_concepts, insights, relationships, evidence]):
            synthesis.update({
                'main_themes': ["Document processing encountered issues"],
                'key_principles': ["Content extraction incomplete"],
                'critical_insights': ["AI analysis failed - manual review recommended"],
                'actionable_takeaways': ["Retry processing with different model", "Check document format and content"],
                'mental_models': [],
                'concept_connections': [],
                'note': 'Generated minimal fallback synthesis - original content analysis failed'
            })
        
        return synthesis
    
    def _extract_themes(self, concepts: List[Any]) -> List[str]:
        """Extract main themes from concepts"""
        # Simple extraction - in practice this could be more sophisticated
        themes = []
        for concept in concepts[:5]:
            if isinstance(concept, dict) and 'description' in concept:
                themes.append(concept['description'])
            elif isinstance(concept, str):
                themes.append(concept)
        return themes
    
    def _extract_principles(self, concepts: List[Any]) -> List[str]:
        """Extract key principles from concepts"""
        principles = []
        for concept in concepts[:7]:
            if isinstance(concept, dict) and 'description' in concept:
                principles.append(concept['description'])
            elif isinstance(concept, str):
                principles.append(concept)
        return principles
    
    def _extract_actionable(self, insights: List[Any]) -> List[str]:
        """Extract actionable takeaways from insights"""
        actionable = []
        for insight in insights[:7]:
            if isinstance(insight, dict) and 'description' in insight:
                actionable.append(insight['description'])
            elif isinstance(insight, str):
                actionable.append(insight)
        return actionable
    
    def _extract_mental_models(self, concepts: List[Any]) -> List[str]:
        """Extract mental models from concepts"""
        models = []
        for concept in concepts[:5]:
            if isinstance(concept, dict) and 'description' in concept:
                models.append(f"Think about: {concept['description']}")
            elif isinstance(concept, str):
                models.append(f"Consider: {concept}")
        return models
