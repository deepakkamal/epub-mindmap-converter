"""
Notes generator for creating explanatory text to accompany mind maps
"""

import json
import logging
from typing import Dict, Any, List
from .web_config import Config

logger = logging.getLogger(__name__)

class MindMapNotesGenerator:
    """
    Generates clear, concise explanatory notes to accompany mind maps
    for readers who haven't read the source material
    """
    
    def __init__(self, openai_client, model: str):
        """
        Initialize notes generator
        
        Args:
            openai_client: OpenAI client instance
            model: AI model to use
        """
        self.client = openai_client
        self.model = model
        self.config = Config()
    
    def generate_mindmap_notes(self, results: Dict[str, Any], mindmap_content: str) -> str:
        """
        Generate comprehensive notes to accompany a mind map
        
        Args:
            results: Complete analysis results from processing
            mindmap_content: The generated mind map content
            
        Returns:
            Formatted notes as markdown string
        """
        logger.info("Generating explanatory notes for mind map")
        
        try:
            # Extract key information for notes
            synthesis = results.get('synthesis', {})
            metadata = results.get('metadata', {})
            
            # Generate notes using AI
            notes_prompt = self._build_notes_prompt(synthesis, metadata, mindmap_content)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": notes_prompt}],
                temperature=0.3
            )
            
            notes_content = response.choices[0].message.content
            
            # Format and structure the notes
            formatted_notes = self._format_notes(notes_content, metadata)
            
            logger.info("[OK] Successfully generated mind map notes")
            return formatted_notes
            
        except Exception as e:
            logger.error(f"Error generating mind map notes: {str(e)}")
            return self._create_fallback_notes(synthesis, metadata, mindmap_content)

    def _format_enhanced_notes(self, notes_content: str, metadata: Dict[str, Any], capture_analysis: Dict[str, Any] = None) -> str:
        """
        Format enhanced notes with comprehensive summary integration
        
        Args:
            notes_content: Generated notes content
            metadata: Document metadata
            capture_analysis: CAPTURE framework analysis
            
        Returns:
            Enhanced formatted notes
        """
        title = metadata.get('title', 'Document')
        
        # Add comprehensive summary section if CAPTURE analysis available
        comprehensive_section = ""
        if capture_analysis and 'capture_analysis' in capture_analysis:
            capture_data = capture_analysis.get('capture_analysis', {})
            comprehensive_summary = capture_data.get('comprehensive_summary', '')
            
            if comprehensive_summary:
                comprehensive_section = f"""

---

## 📚 Comprehensive Chapter Summary

{comprehensive_summary}

---
"""
        
        # Add metadata and enhanced formatting
        timestamp = metadata.get('processing_timestamp', 'Unknown')
        capture_used = metadata.get('capture_framework_applied', False)
        framework_note = " using CAPTURE Framework" if capture_used else ""
        
        formatted_notes = f"""# Mind Map Notes: {title}

{notes_content}

{comprehensive_section}

---

## 📋 Analysis Information

**Generated**: {timestamp}{framework_note}  
**Study Tip**: Use this mind map and notes together for best comprehension. The mind map shows relationships, while these notes provide detailed explanations.

**Comprehension Strategy Used**: {"CAPTURE Framework (Comprehension, Analysis, Partitioning, Thematic extraction, Unified synthesis, Response generation, Explanation strategies)" if capture_used else "Traditional analysis"}
"""
        
        return formatted_notes
    
    def _build_notes_prompt(self, synthesis: Dict[str, Any], metadata: Dict[str, Any], mindmap_content: str) -> str:
        """
        Build prompt for generating explanatory notes
        
        Args:
            synthesis: Synthesized insights
            metadata: Document metadata
            mindmap_content: Mind map structure
            
        Returns:
            Formatted prompt
        """
        title = metadata.get('title', 'Document Analysis')
        
        # Prepare synthesis summary
        synthesis_summary = {
            'main_themes': synthesis.get('main_themes', [])[:6],
            'key_principles': synthesis.get('key_principles', [])[:6],
            'critical_insights': synthesis.get('critical_insights', [])[:6],
            'actionable_takeaways': synthesis.get('actionable_takeaways', [])[:6]
        }
        
        return f"""
        Create clear, engaging explanatory notes to accompany this mind map.
        
        Document: {title}
        
        Mind Map Structure:
        {mindmap_content}
        
        Synthesis Data:
        {json.dumps(synthesis_summary, indent=2)[:3000]}
        
        TARGET AUDIENCE: Students who haven't read the original book/chapter
        
        REQUIREMENTS:
        1. Write in clear, accessible language (high school level)
        2. Explain each major branch of the mind map
        3. Provide context and background for key concepts
        4. Include specific examples and applications
        5. Make connections between different parts explicit
        6. Use engaging, conversational tone
        7. Length: 300-500 words total
        8. Structure with clear headings
        
        FORMAT:
        # Mind Map Explanation: [Title]
        
        ## Overview
        [2-3 sentences explaining what this chapter/document is about]
        
        ## Key Themes Explained
        
        ### [Theme 1 from mind map]
        [Explain this theme clearly with examples]
        
        ### [Theme 2 from mind map]  
        [Explain this theme clearly with examples]
        
        [Continue for major themes...]
        
        ## Practical Applications
        [How can students use these insights in real life?]
        
        ## Key Takeaways
        [3-5 bullet points of most important points]
        
        TONE: Clear, engaging, educational - like a good teacher explaining complex ideas simply.
        """

    def _build_capture_enhanced_notes_prompt(self, synthesis: Dict[str, Any], metadata: Dict[str, Any], mindmap_content: str, capture_analysis: Dict[str, Any]) -> str:
        """
        Build enhanced notes prompt using CAPTURE framework analysis
        
        Args:
            synthesis: Synthesized insights
            metadata: Document metadata
            mindmap_content: Mind map content
            capture_analysis: CAPTURE framework analysis
            
        Returns:
            Enhanced prompt for notes generation
        """
        title = metadata.get('title', 'Document')
        
        # Extract CAPTURE components
        capture_data = capture_analysis.get('capture_analysis', {})
        structure_analysis = capture_data.get('structure_analysis', {})
        pattern_analysis = capture_data.get('pattern_analysis', {})
        thematic_analysis = capture_data.get('thematic_analysis', {})
        unified_synthesis = capture_data.get('unified_synthesis', {})
        explanation_strategies = capture_data.get('explanation_strategies', {})
        
        # Prepare synthesis summary
        synthesis_summary = {
            'main_themes': synthesis.get('main_themes', [])[:6],
            'key_principles': synthesis.get('key_principles', [])[:6],
            'critical_insights': synthesis.get('critical_insights', [])[:6]
        }
        
        return f"""
        Create comprehensive, educational notes using CAPTURE framework analysis to accompany this mind map.
        
        Document: {title}
        
        Mind Map Structure:
        {mindmap_content}
        
        CAPTURE Framework Analysis:
        - Text Structure: {structure_analysis.get('primary_structure', 'mixed')}
        - Primary Themes: {thematic_analysis.get('primary_themes', [])[:3]}
        - SWBST Pattern: {pattern_analysis.get('swbst_analysis', {})}
        - Core Concepts: {unified_synthesis.get('core_concepts', [])[:5]}
        
        Traditional Synthesis:
        {json.dumps(synthesis_summary, indent=2)[:2000]}
        
        TARGET AUDIENCE: Students who haven't read the original content but need deep understanding
        
        CAPTURE-ENHANCED REQUIREMENTS:
        1. Write in clear, accessible language (high school to college level)
        2. Use comprehension strategy language where appropriate (cause-effect, problem-solution, SWBST)
        3. Explain each major branch using the identified text structure
        4. Provide context and background for key concepts
        5. Include specific examples and applications
        6. Make connections between different parts explicit using structure analysis
        7. Use engaging, educational tone that teaches comprehension strategies
        8. Length: 400-600 words total
        9. Structure with clear headings that reflect the text structure
        
        ENHANCED FORMAT:
        # Mind Map Explanation: [Title]
        
        ## Document Structure & Approach
        [Explain the primary text structure and how it helps understanding - 2-3 sentences]
        
        ## Overview
        [2-3 sentences explaining what this chapter/document is about, incorporating structure awareness]
        
        ## Key Concepts Explained
        [Use the identified text structure to organize explanations]
        
        ### [Concept 1 from mind map - using structure-appropriate language]
        [Explain using cause-effect, problem-solution, or comparison language as appropriate]
        
        ### [Concept 2 from mind map - using structure-appropriate language]  
        [Explain with focus on relationships and patterns]
        
        [Continue for major concepts...]
        
        ## Comprehension Connections
        [How the concepts connect using SWBST or cause-effect patterns if identified]
        
        ## Practical Applications
        [How can students use these insights, including comprehension strategies]
        
        ## Key Takeaways & Study Strategies
        [4-6 bullet points of most important points plus how to study this type of content]
        
        TONE: Educational, clear, strategy-focused - like an expert teacher explaining both content AND how to understand complex material.
        """
    
    def _format_notes(self, notes_content: str, metadata: Dict[str, Any]) -> str:
        """
        Format the generated notes with proper structure
        
        Args:
            notes_content: Raw notes from AI
            metadata: Document metadata
            
        Returns:
            Formatted notes string
        """
        title = metadata.get('title', 'Document Analysis')
        
        # Add header information
        formatted = f"""# Mind Map Explanation: {title}

---

{notes_content}

---
"""
        return formatted
    
    def _create_fallback_notes(self, results: Dict[str, Any], mindmap_content: str) -> str:
        """
        Create basic notes when AI generation fails
        
        Args:
            results: Analysis results
            mindmap_content: Mind map content
            
        Returns:
            Basic formatted notes
        """
        logger.info("Creating fallback notes")
        
        metadata = results.get('metadata', {})
        synthesis = results.get('synthesis', {})
        title = metadata.get('title', 'Document Analysis')
        
        notes = f"""# Mind Map Explanation: {title}

## Overview
This mind map represents the key concepts and insights extracted from the document using AI analysis.

## Main Themes
"""
        
        # Add main themes if available
        themes = synthesis.get('main_themes', [])
        for i, theme in enumerate(themes[:4], 1):
            theme_text = self._extract_text_from_item(theme)
            notes += f"\n### Theme {i}: {theme_text}\n"
            notes += "This represents one of the core ideas presented in the document.\n"
        
        # Add key principles
        principles = synthesis.get('key_principles', [])
        if principles:
            notes += "\n## Key Principles\n"
            for principle in principles[:3]:
                principle_text = self._extract_text_from_item(principle)
                notes += f"- {principle_text}\n"
        
        # Add actionable takeaways
        takeaways = synthesis.get('actionable_takeaways', [])
        if takeaways:
            notes += "\n## What You Can Do\n"
            for takeaway in takeaways[:3]:
                takeaway_text = self._extract_text_from_item(takeaway)
                notes += f"- {takeaway_text}\n"
        
        return notes
    
    def _extract_text_from_item(self, item: Any) -> str:
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
                    return str(item[field])[:100]  # Limit length
            return str(item)[:100]
        elif isinstance(item, str):
            return item[:100]
        else:
            return str(item)[:100]

    def generate_student_summary(self, results: Dict[str, Any]) -> str:
        """
        Generate a comprehensive summary using CAPTURE framework when available
        
        Args:
            results: Analysis results
            
        Returns:
            Comprehensive summary text
        """
        logger.info("Generating comprehensive student summary")
        
        try:
            synthesis = results.get('synthesis', {})
            capture_analysis = results.get('capture_analysis', {})
            metadata = results.get('metadata', {})
            title = metadata.get('title', 'Document')
            
            # Use CAPTURE framework comprehensive summary if available
            if capture_analysis and 'capture_analysis' in capture_analysis:
                capture_data = capture_analysis.get('capture_analysis', {})
                comprehensive_summary = capture_data.get('comprehensive_summary', '')
                
                if comprehensive_summary:
                    logger.info("Using CAPTURE framework comprehensive summary")
                    return comprehensive_summary + f"\n\n---\n📚 *Use the detailed mind map and notes to dive deeper into these concepts.*"
            
            # Fallback to enhanced summary generation
            summary_prompt = self._build_enhanced_summary_prompt(synthesis, capture_analysis, metadata, title)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator using advanced comprehension strategies. Create thorough summaries that help students understand complex topics using proven frameworks like SWBST, cause-effect analysis, and text structure approaches."},
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            ai_summary = response.choices[0].message.content.strip()
            
            # Add metadata footer
            ai_summary += f"\n\n---\n📚 *Use the detailed mind map and notes to dive deeper into these concepts.*"
            
            return ai_summary
            
        except Exception as e:
            logger.error(f"Error generating student summary: {str(e)}")
            # Fallback to enhanced version of original method
            return self._generate_fallback_summary(results)
    
    def _build_summary_prompt(self, synthesis: Dict[str, Any], metadata: Dict[str, Any], title: str) -> str:
        """Build prompt for AI-generated comprehensive summary"""
        
        prompt = f"""Create a comprehensive but concise summary for "{title}" that helps students understand the key concepts without reading the full text.

Analysis Data:
- Main Themes: {json.dumps(synthesis.get('main_themes', []), indent=2)}
- Key Principles: {json.dumps(synthesis.get('key_principles', []), indent=2)}
- Critical Insights: {json.dumps(synthesis.get('critical_insights', []), indent=2)}
- Actionable Takeaways: {json.dumps(synthesis.get('actionable_takeaways', []), indent=2)}

Requirements:
1. Start with "# Quick Summary: {title}"
2. Include a "## What's This About?" section with 2-3 substantial paragraphs
3. Include a "## Core Concepts" section with 4-6 key concepts explained in 1-2 sentences each
4. Include a "## Key Insights" section with 2-3 important insights
5. Include a "## Why This Matters" section explaining practical relevance
6. Include a "## Main Takeaways" section with 3-5 actionable points

Write in clear, accessible language that a student can understand. Be thorough but concise - aim for substance over brevity. Each section should provide real value and understanding.

Focus on:
- Clear explanations of concepts
- Why these ideas matter
- How they connect to bigger pictures
- Practical applications
- Key evidence or examples mentioned

Total length: 400-600 words."""

        return prompt

    def _build_enhanced_summary_prompt(self, synthesis: Dict[str, Any], capture_analysis: Dict[str, Any], metadata: Dict[str, Any], title: str) -> str:
        """
        Build enhanced summary prompt using CAPTURE framework analysis
        
        Args:
            synthesis: Synthesized insights
            capture_analysis: CAPTURE framework analysis
            metadata: Document metadata
            title: Document title
            
        Returns:
            Enhanced prompt for summary generation
        """
        # Extract CAPTURE components if available
        capture_data = capture_analysis.get('capture_analysis', {}) if capture_analysis else {}
        structure_analysis = capture_data.get('structure_analysis', {})
        pattern_analysis = capture_data.get('pattern_analysis', {})
        thematic_analysis = capture_data.get('thematic_analysis', {})
        unified_synthesis = capture_data.get('unified_synthesis', {})
        
        prompt = f"""Create a comprehensive summary for "{title}" using advanced comprehension strategies.

CAPTURE Framework Analysis Available:
- Text Structure: {structure_analysis.get('primary_structure', 'Not analyzed')}
- SWBST Pattern: {pattern_analysis.get('swbst_analysis', {}) if pattern_analysis else 'Not analyzed'}
- Primary Themes: {len(thematic_analysis.get('primary_themes', [])) if thematic_analysis else 0} identified
- Core Concepts: {len(unified_synthesis.get('core_concepts', [])) if unified_synthesis else 0} identified

Traditional Analysis Data:
- Main Themes: {json.dumps(synthesis.get('main_themes', []), indent=2)}
- Key Principles: {json.dumps(synthesis.get('key_principles', []), indent=2)}
- Critical Insights: {json.dumps(synthesis.get('critical_insights', []), indent=2)}
- Actionable Takeaways: {json.dumps(synthesis.get('actionable_takeaways', []), indent=2)}

ENHANCED SUMMARY REQUIREMENTS:
1. Start with "# Comprehensive Summary: {title}"

2. **Executive Overview** (2-3 substantial paragraphs)
   - What this content is about and why it matters
   - Main purpose and target audience
   - Key value proposition and outcomes

3. **Structure & Organization** (if structure analysis available)
   - Describe the primary text structure (problem-solution, cause-effect, comparison, etc.)
   - How this structure helps understanding
   - Key organizing principles

4. **Core Concepts & Frameworks** (organized by importance)
   - Essential concepts with clear explanations
   - Mental models and frameworks presented
   - How concepts relate to each other
   - Include SWBST analysis if applicable (Somebody-Wanted-But-So-Then)

5. **Cause-Effect Relationships** (if identified)
   - Key causal chains and their significance
   - Consequences and implications
   - How understanding these helps with comprehension

6. **Problem-Solution Patterns** (if identified)
   - Main problems addressed
   - Solutions provided and their effectiveness
   - Lessons learned and applications

7. **Key Insights & Discoveries**
   - Most important insights and their implications
   - New perspectives or ways of thinking
   - Critical connections and patterns

8. **Practical Applications**
   - How to apply these concepts in real situations
   - Specific examples and use cases
   - Implementation strategies and tips

9. **Main Takeaways**
   - 6-8 most important points to remember
   - Action items and next steps
   - Success indicators and assessment criteria

WRITING APPROACH:
- Use clear, accessible language (high school to early college level)
- Incorporate comprehension strategies terminology where helpful
- Show relationships between concepts explicitly
- Include specific examples and evidence
- Make connections to real-world applications
- Use engaging headings and clear transitions
- Aim for 700-900 words total for comprehensive coverage

Focus on creating a summary that not only informs but also teaches students HOW to understand and work with complex material using proven comprehension frameworks."""

        return prompt
    
    def _generate_fallback_summary(self, results: Dict[str, Any]) -> str:
        """Generate enhanced fallback summary if AI fails"""
        synthesis = results.get('synthesis', {})
        metadata = results.get('metadata', {})
        title = metadata.get('title', 'Document')
        
        summary = f"""# Quick Summary: {title}

## What's This About?
"""
        
        # Enhanced main themes section
        themes = synthesis.get('main_themes', [])
        if themes:
            summary += f"This chapter explores {len(themes)} interconnected themes that form a comprehensive framework for understanding the topic. "
            
            for i, theme in enumerate(themes[:4]):  # Show more themes
                theme_text = self._extract_detailed_text(theme)
                summary += f"**{i+1}.** {theme_text} "
            
            if len(themes) > 4:
                summary += f"along with {len(themes) - 4} additional supporting concepts."
            summary += "\n\n"
        
        # Add core principles
        principles = synthesis.get('key_principles', [])
        if principles:
            summary += "## Core Principles\n"
            for i, principle in enumerate(principles[:3]):
                principle_text = self._extract_detailed_text(principle)
                summary += f"• {principle_text}\n"
            summary += "\n"
        
        # Enhanced insights section
        insights = synthesis.get('critical_insights', [])
        if insights:
            summary += "## Key Insights\n"
            for i, insight in enumerate(insights[:3]):
                insight_text = self._extract_detailed_text(insight)
                summary += f"**{i+1}.** {insight_text}\n"
            summary += "\n"
        
        # Enhanced takeaways section
        takeaways = synthesis.get('actionable_takeaways', [])
        if takeaways:
            summary += "## Main Takeaways\n"
            for i, takeaway in enumerate(takeaways[:4]):
                takeaway_text = self._extract_detailed_text(takeaway)
                summary += f"• {takeaway_text}\n"
            summary += "\n"
        
        summary += "📚 *Use the detailed mind map and notes to dive deeper into these concepts.*"
        
        return summary
    
    def _extract_detailed_text(self, item) -> str:
        """Extract more detailed text from synthesis items"""
        if isinstance(item, dict):
            # Try different possible keys for more detailed content
            for key in ['description', 'content', 'text', 'summary', 'title']:
                if key in item and item[key]:
                    return str(item[key])[:300]  # Increased from 100 to 300 chars
            return str(item)[:300]
        elif isinstance(item, str):
            return item[:300]  # Increased from 100 to 300 chars
        else:
            return str(item)[:300]
