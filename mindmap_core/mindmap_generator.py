"""
Mind map generation module for creating Mermaid diagrams
"""

import json
import logging
from typing import Dict, Any
from .web_config import Config

logger = logging.getLogger(__name__)

class MindMapGenerator:
    """
    Generates Mermaid mind maps from extracted insights
    """
    
    def __init__(self, openai_client, model: str):
        """
        Initialize mind map generator
        
        Args:
            openai_client: OpenAI client instance
            model: AI model to use
        """
        self.client = openai_client
        self.model = model
        self.config = Config()
        self.mindmap_config = self.config.MINDMAP_CONFIG
        
    def generate_mindmap_from_synthesis(self, insights: Dict[str, Any], mindmap_type: str = "comprehensive") -> str:
        """
        Generate mind map from synthesized insights with CAPTURE framework enhancement
        
        Args:
            insights: Complete insights dictionary
            mindmap_type: Type of mind map (main, actionable, relationship, comprehensive)
            
        Returns:
            Mermaid mind map as string
        """
        synthesis = insights.get('synthesis', {})
        capture_analysis = insights.get('capture_analysis', {})
        title = insights.get('metadata', {}).get('title', 'Document Analysis')
        
        logger.info(f"Generating {mindmap_type} mind map for: {title}")
        
        if 'error' in synthesis:
            logger.warning("Synthesis contains errors, creating basic mind map")
            return self._create_basic_mindmap(insights, title)
        
        try:
            # Use CAPTURE analysis if available for enhanced mindmap generation
            if capture_analysis and 'capture_analysis' in capture_analysis:
                logger.info("Using CAPTURE framework for enhanced mindmap generation")
                return self._generate_capture_enhanced_mindmap(synthesis, capture_analysis, title, mindmap_type)
            else:
                return self._generate_ai_mindmap(synthesis, title, mindmap_type)
        except Exception as e:
            logger.error(f"Error generating AI mind map: {str(e)}")
            return self._create_fallback_mindmap(synthesis, title)
    
    def _generate_ai_mindmap(self, synthesis: Dict[str, Any], title: str, mindmap_type: str = "comprehensive") -> str:
        """
        Generate mind map using AI
        
        Args:
            synthesis: Synthesized insights
            title: Document title
            mindmap_type: Type of mind map to generate
            
        Returns:
            Cleaned Mermaid mind map string
        """
        prompt = self._build_mindmap_prompt(synthesis, title, mindmap_type)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        raw_content = response.choices[0].message.content
        
        # Clean and standardize the GPT output
        return self._clean_gpt_mindmap_output(raw_content, title)
    
    def _build_mindmap_prompt(self, synthesis: Dict[str, Any], title: str, mindmap_type: str = "comprehensive") -> str:
        """
        Build prompt for mind map generation
        
        Args:
            synthesis: Synthesized insights
            title: Document title
            
        Returns:
            Formatted prompt
        """
        # Prepare synthesis data for prompt
        synthesis_summary = {
            'main_themes': synthesis.get('main_themes', [])[:6],
            'key_principles': synthesis.get('key_principles', [])[:8],
            'critical_insights': synthesis.get('critical_insights', [])[:6],
            'actionable_takeaways': synthesis.get('actionable_takeaways', [])[:6]
        }
        
        return f"""
        Create a rich, detailed Mermaid mindmap that captures the specific insights and key concepts from this document analysis.
        
        Document: {title}
        
        Synthesis Data:
        {json.dumps(synthesis_summary, indent=2)[:3000]}
        
        CORRECT MERMAID MINDMAP SYNTAX:
        1. Output ONLY the raw mindmap content (no code fences)
        2. Start with exactly "mindmap" as the first line
        3. Root node format: root((Title Here)) - use DOUBLE parentheses
        4. Branches: Just text with indentation - NO brackets needed for simple branches
        5. Create EXACTLY ONE root node only
        6. All major concepts must be direct branches under the single root
        7. Extract SPECIFIC concepts, processes, and mechanisms from the content
        8. Use the exact terminology and language from the source material
        9. Focus on concrete details rather than abstract categories
        10. Include actionable insights and practical applications

        CORRECT STRUCTURE EXAMPLE:
        mindmap
            root((Document Title))
                Major Concept 1
                    Sub-concept A
                    Sub-concept B
                Major Concept 2
                    Sub-concept C
                    Sub-concept D
                Major Concept 3
                    Sub-concept E
        
        SYNTAX RULES:
        - Root: root((text)) with double parentheses
        - Branches: Simple text with 4-space indentation
        - No colons, no descriptions after node names
        - Keep node names concise (2-5 words max)
        - Use clear, specific terminology from the content
        
        AVOID generic organizational labels like:
        - "Main Themes", "Key Principles", "Critical Insights", "Actionable Takeaways"
        - "Important Points", "Core Concepts", "Overview"
        - Abstract wrapper terms that don't add content value
        
        INSTEAD extract and use:
        - The actual concepts, processes, and mechanisms mentioned in the content
        - Domain-specific terminology and specialized vocabulary
        - Concrete examples, cases, and specific instances
        - Detailed steps, procedures, and methodologies
        - Specific relationships, patterns, and dynamics described
        - Practical applications and real-world implementations
        
        Structure approach:
        - Use the most important SPECIFIC concepts as main branches
        - Break down complex ideas into their component parts
        - Show relationships and dependencies between concepts
        - Include concrete examples and applications as sub-nodes
        - Focus on what makes THIS content unique and valuable
        - For every node, add a short explanation after a colon
        
        Extract the richest, most specific content from the synthesis data.
        Look for the specialized knowledge, detailed processes, and unique insights.
        Every node should contain meaningful, content-specific information and a short explanation.
        
        CRITICAL: Output only the mindmap content without any markdown code fences, explanations, or extra text.
        Start directly with "mindmap" and focus on the specific richness of the actual content. For every node, add a short explanation after a colon.
        """
    
    def _generate_capture_enhanced_mindmap(self, synthesis: Dict[str, Any], capture_analysis: Dict[str, Any], title: str, mindmap_type: str = "comprehensive") -> str:
        """
        Generate enhanced mind map using CAPTURE framework analysis
        
        Args:
            synthesis: Synthesized insights
            capture_analysis: CAPTURE framework analysis results
            title: Document title
            mindmap_type: Type of mind map to generate
            
        Returns:
            Enhanced Mermaid mind map string
        """
        prompt = self._build_capture_enhanced_prompt(synthesis, capture_analysis, title, mindmap_type)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        raw_content = response.choices[0].message.content
        
        # Clean and standardize the GPT output
        return self._clean_gpt_mindmap_output(raw_content, title)
    
    def _build_capture_enhanced_prompt(self, synthesis: Dict[str, Any], capture_analysis: Dict[str, Any], title: str, mindmap_type: str = "comprehensive") -> str:
        """
        Build enhanced prompt using CAPTURE framework analysis
        
        Args:
            synthesis: Synthesized insights
            capture_analysis: CAPTURE framework analysis
            title: Document title
            mindmap_type: Type of mind map
            
        Returns:
            Enhanced prompt for mindmap generation
        """
        # Extract CAPTURE components
        capture_data = capture_analysis.get('capture_analysis', {})
        structure_analysis = capture_data.get('structure_analysis', {})
        pattern_analysis = capture_data.get('pattern_analysis', {})
        thematic_analysis = capture_data.get('thematic_analysis', {})
        unified_synthesis = capture_data.get('unified_synthesis', {})
        
        # Prepare comprehensive data for prompt
        enhanced_data = {
            'main_themes': synthesis.get('main_themes', [])[:6],
            'key_principles': synthesis.get('key_principles', [])[:8],
            'critical_insights': synthesis.get('critical_insights', [])[:6],
            'actionable_takeaways': synthesis.get('actionable_takeaways', [])[:6],
            'text_structure': structure_analysis.get('primary_structure', 'mixed'),
            'swbst_framework': pattern_analysis.get('swbst_analysis', {}),
            'cause_effect_chains': pattern_analysis.get('cause_effect_chains', [])[:5],
            'problem_solutions': pattern_analysis.get('problem_solution_pairs', [])[:5],
            'primary_themes': thematic_analysis.get('primary_themes', [])[:4],
            'core_concepts': unified_synthesis.get('core_concepts', [])[:8]
        }
        
        return f"""
        Create an enhanced Mermaid mindmap using CAPTURE framework analysis for comprehensive understanding.
        
        Document: {title}
        Text Structure: {enhanced_data['text_structure']}
        
        Enhanced Analysis Data:
        {json.dumps(enhanced_data, indent=2)[:4000]}
        
        CORRECT MERMAID MINDMAP SYNTAX:
        1. Output ONLY the raw mindmap content (no code fences)
        2. Start with exactly "mindmap" as the first line
        3. Root node format: root((Title Here)) - use DOUBLE parentheses
        4. Branches: Just text with indentation - NO brackets needed
        5. Create EXACTLY ONE root node only
        6. All major concepts, themes, and analysis sections must be direct branches under the single root
        
        CORRECT STRUCTURE EXAMPLE:
        mindmap
            root((Document Title))
                Problem Analysis
                    Specific Problem 1
                    Specific Problem 2
                Solution Framework
                    Specific Solution 1
                    Specific Solution 2
                Outcomes and Implications
                    Outcome 1
                    Outcome 2
        
        SYNTAX RULES:
        - Root: root((text)) with double parentheses
        - Branches: Simple text with 4-space indentation
        - No colons, no descriptions after node names
        - Keep node names concise (2-5 words max)
        - Use clear, specific terminology from the content
        
        STRUCTURE-BASED ORGANIZATION:
        - Use text structure analysis to organize main branches
        - For Problem-Solution texts: organize by problems → solutions → outcomes
        - For Cause-Effect texts: organize by causes → effects → implications
        - For Comparison texts: organize by comparison points → similarities → differences
        - For mixed structures: use unified synthesis core concepts as main branches
        
        SWBST FRAMEWORK INTEGRATION:
        - If applicable, use Somebody-Wanted-But-So-Then pattern to show:
          * Key actors/subjects (Somebody)
          * Goals and objectives (Wanted)  
          * Obstacles and challenges (But)
          * Actions and solutions (So)
          * Results and outcomes (Then)
        
        ENHANCED EXPLANATION STRATEGY:
        - For each main branch: add detailed explanation (10-20 words) after colon
        - For sub-branches: add context explanation (5-15 words) after colon
        - Use cause-effect language: "leads to", "results in", "because of"
        - Use problem-solution language: "solves", "addresses", "prevents"
        - Include practical applications and real-world connections
        
        CONTENT RICHNESS:
        - Extract SPECIFIC concepts, processes, and mechanisms
        - Use exact terminology from the source material
        - Include concrete examples and evidence
        - Show relationships between concepts clearly
        - Focus on actionable insights and applications
        
        AVOID generic labels. INSTEAD use:
        - Actual concept names and terminology
        - Specific processes and methodologies
        - Concrete examples and case studies
        - Detailed cause-effect relationships
        - Practical implementation strategies
        
        CRITICAL: Output only the mindmap content without any markdown code fences.
        Start directly with "mindmap" and use the text structure and CAPTURE analysis to create a comprehensive, well-explained mindmap.
        Every node should have meaningful explanations that help students understand the concepts and their relationships.
        """
    
    def _create_basic_mindmap(self, insights: Dict[str, Any], title: str) -> str:
        """
        Create basic mind map when synthesis is not available
        
        Args:
            insights: Raw insights dictionary
            title: Document title
            
        Returns:
            Basic Mermaid mind map
        """
        logger.info("Creating basic mind map from raw insights")
        
        # Extract some concepts from chunk analyses
        concepts = []
        chunk_analyses = insights.get('chunk_analyses', [])
        
        for chunk_data in chunk_analyses[:3]:  # Use first 3 chunks
            analysis = chunk_data.get('analysis', {})
            if 'key_concepts' in analysis:
                concepts.extend(analysis['key_concepts'][:2])
        
        # Create simple mind map (no code fences)
        short_title = self._shorten_title(title)
        mindmap = f"""mindmap
  root){short_title}(
    Key Concepts"""
        
        for i, concept in enumerate(concepts[:6]):
            concept_text = self._extract_concept_text(concept)
            mindmap += f"\n      Concept {i+1}: {concept_text[:30]}"
        
        mindmap += "\n    Analysis Results"
        mindmap += f"\n      {len(chunk_analyses)} sections analyzed"
        mindmap += "\n      Insights extracted"
        
        return mindmap
    
    def _create_fallback_mindmap(self, synthesis: Dict[str, Any], title: str) -> str:
        """
        Create fallback mind map from synthesis data
        
        Args:
            synthesis: Synthesis dictionary
            title: Document title
            
        Returns:
            Fallback Mermaid mind map
        """
        logger.info("Creating fallback mind map")
        
        short_title = self._shorten_title(title)
        mindmap = f"""mindmap
  root){short_title}("""
        
        # Add main themes
        themes = synthesis.get('main_themes', [])
        if themes:
            mindmap += "\n    Main Themes"
            for theme in themes[:4]:
                theme_text = self._extract_text(theme)
                mindmap += f"\n      {theme_text[:40]}"
        
        # Add key principles
        principles = synthesis.get('key_principles', [])
        if principles:
            mindmap += "\n    Key Principles"
            for principle in principles[:4]:
                principle_text = self._extract_text(principle)
                mindmap += f"\n      {principle_text[:40]}"
        
        # Add actionable takeaways
        takeaways = synthesis.get('actionable_takeaways', [])
        if takeaways:
            mindmap += "\n    Action Items"
            for takeaway in takeaways[:4]:
                takeaway_text = self._extract_text(takeaway)
                mindmap += f"\n      {takeaway_text[:40]}"
        
        return mindmap
    
    def generate_detailed_mindmap(self, insights: Dict[str, Any]) -> str:
        """
        Generate detailed mind map with relationships
        
        Args:
            insights: Complete insights dictionary
            
        Returns:
            Detailed Mermaid flowchart
        """
        synthesis = insights.get('synthesis', {})
        title = insights.get('metadata', {}).get('title', 'Analysis')
        
        try:
            prompt = f"""
            Create a detailed Mermaid flowchart showing relationships between concepts from "{title}".
            
            Data: {json.dumps(synthesis, indent=2)[:2500]}
            
            Use flowchart syntax with:
            - Rectangular nodes [Concept]
            - Diamond decisions {{Decision}}
            - Arrows showing relationships -->
            - Different arrow types for different relationships
            
            Show:
            1. Main concepts and how they connect
            2. Cause-effect relationships  
            3. Decision points or key choices
            4. Outcomes or results
            
            Keep it readable with 15-20 nodes maximum.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating detailed mind map: {str(e)}")
            return self._create_simple_flowchart(synthesis, title)
    
    def _create_simple_flowchart(self, synthesis: Dict[str, Any], title: str) -> str:
        """Create simple flowchart as fallback"""
        flowchart = f"""flowchart TD
    A[{self._shorten_title(title)}] --> B[Main Themes]
    A --> C[Key Principles]
    A --> D[Action Items]"""
        
        themes = synthesis.get('main_themes', [])
        if themes:
            flowchart += f"\n    B --> E[{self._extract_text(themes[0])[:30]}]"
        
        return flowchart
    
    def _shorten_title(self, title: str) -> str:
        """Shorten title for mind map root"""
        words = title.replace('_', ' ').replace('-', ' ').split()
        if len(words) <= 4:
            return ' '.join(words).title()
        return ' '.join(words[:4]).title()
    
    def _extract_concept_text(self, concept) -> str:
        """Extract text from concept object"""
        if isinstance(concept, dict):
            return concept.get('description', concept.get('name', str(concept)))
        return str(concept)
    
    def _extract_text(self, item) -> str:
        """Extract text from various item formats"""
        if isinstance(item, dict):
            return item.get('description', item.get('text', item.get('content', str(item))))
        return str(item)[:50]  # Limit length
    
    def _clean_gpt_mindmap_output(self, raw_content: str, title: str) -> str:
        """
        Clean and standardize GPT-generated mindmap content
        
        Args:
            raw_content: Raw content from GPT
            title: Document title for fallback
            
        Returns:
            Clean mindmap content ready for API
        """
        import re
        
        if not raw_content:
            return self._create_simple_fallback(title)
        
        content = str(raw_content).strip()
        
        # Remove any markdown code fences if GPT added them despite instructions
        content = re.sub(r'```mermaid\s*\n?', '', content)
        content = re.sub(r'```\s*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'```', '', content)
        
        # Clean up the content
        lines = content.split('\n')
        cleaned_lines = []
        found_mindmap = False
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines and explanatory text
            if not stripped or stripped.startswith('Here') or stripped.startswith('This'):
                continue
                
            # Find the mindmap start
            if stripped == 'mindmap' or stripped.startswith('mindmap'):
                if not found_mindmap:
                    cleaned_lines.append('mindmap')
                    found_mindmap = True
                continue
                
            # Skip duplicate mindmap declarations
            if stripped == 'mindmap' and found_mindmap:
                continue
                
            # Only include content after we found mindmap
            if found_mindmap:
                cleaned_lines.append(line)
        
        if not found_mindmap or len(cleaned_lines) < 3:
            logger.warning("GPT output didn't contain valid mindmap, creating fallback")
            return self._create_simple_fallback(title)
        
        result = '\n'.join(cleaned_lines)
        
        # Ensure proper root format
        result = self._standardize_root_format(result, title)
        
        logger.info(f"Cleaned GPT mindmap: {len(result)} characters, {len(cleaned_lines)} lines")
        return result
    
    def _standardize_root_format(self, content: str, title: str) -> str:
        """Ensure the root format is consistent and uses correct Mermaid syntax"""
        lines = content.split('\n')
        result_lines = ['mindmap']  # Start fresh with mindmap declaration
        
        # Find all root nodes and collect their content
        root_sections = []
        current_section = []
        main_root_found = False
        main_root_line = None
        
        for i, line in enumerate(lines):
            if i == 0 and line.strip() == 'mindmap':
                continue  # Skip the mindmap declaration, we already added it
                
            stripped = line.strip()
            
            # Check if this is a root node line (handle both old and new syntax)
            is_root = (stripped.startswith('root((') and stripped.endswith('))')) or \
                     (stripped.startswith('root)') and stripped.endswith('('))
            
            if is_root:
                # Save previous section if exists
                if current_section:
                    root_sections.append(current_section)
                    current_section = []
                
                # Process the root line and convert to CORRECT syntax
                if stripped.startswith('root((') and stripped.endswith('))'):
                    # Already correct format
                    root_text = stripped[6:-2]  # Extract text between root(( and ))
                    root_line = f'root(({root_text}))'
                elif stripped.startswith('root)') and stripped.endswith('('):
                    # Convert old format root)text( to correct root((text))
                    root_text = stripped[5:-1]  # Extract text between root) and (
                    root_line = f'root(({root_text}))'
                
                if not main_root_found:
                    # This is our main (and only) root - use correct indentation
                    main_root_line = f'    {root_line}'  # 4 spaces for proper indentation
                    main_root_found = True
                else:
                    # This is an additional root - convert to branch
                    branch_name = root_text  # Use the extracted text as branch name
                    current_section.append(f'        {branch_name}')  # 8 spaces for branch
            else:
                # Regular content line - clean up any description colons
                if ':' in stripped and stripped.count(':') == 1:
                    # Remove descriptions after colons to keep node names clean
                    node_name = stripped.split(':')[0].strip()
                    if node_name:
                        # Keep original indentation but use clean node name
                        indent = len(line) - len(line.lstrip())
                        current_section.append(' ' * indent + node_name)
                else:
                    current_section.append(line)
        
        # Add the last section
        if current_section:
            root_sections.append(current_section)
        
        # If no root was found, create one
        if not main_root_found:
            short_title = self._shorten_title(title)
            main_root_line = f'    root(({short_title}))'  # Correct syntax with proper indentation
        
        # Build the final result
        result_lines.append(main_root_line)
        
        # Add all content sections
        for section in root_sections:
            for line in section:
                if line.strip():  # Skip empty lines
                    result_lines.append(line)
        
        # If we fixed multiple roots, log it
        num_roots = sum(1 for line in lines if 
                       line.strip().startswith('root((') or 
                       (line.strip().startswith('root)') and line.strip().endswith('(')))
        
        if num_roots > 1:
            logger.info(f"Fixed {num_roots} root nodes -> 1 root with {num_roots-1} main branches")
        
        return '\n'.join(result_lines)
    
    def _create_simple_fallback(self, title: str) -> str:
        """Create a simple fallback mindmap with correct syntax"""
        short_title = self._shorten_title(title)
        return f"""mindmap
    root(({short_title}))
        Key Insights
            Analysis completed
            Insights extracted
        Summary
            Document processed
            Results available"""
