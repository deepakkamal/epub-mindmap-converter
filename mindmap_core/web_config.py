#!/usr/bin/env python3
"""
Web Interface Configuration for Mind Map Creator

This module provides configuration that integrates with the web interface,
eliminating hardcoded model restrictions.
"""

import os
import sys
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import shared configuration from web interface
current_dir = Path(__file__).parent.parent.parent.parent
web_interface_dir = current_dir / "web_interface"
sys.path.insert(0, str(web_interface_dir))

try:
    from shared_config import SharedModelConfig
    SHARED_CONFIG_AVAILABLE = True
except ImportError:
    SHARED_CONFIG_AVAILABLE = False
    print("Warning: Could not import shared configuration from web interface")

class Config:
    """Configuration that pulls everything from the web interface"""
    
    # API Settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-5-mini")
    
    # Processing Settings
    MAX_TOKENS_PER_CHUNK = int(os.getenv("MAX_TOKENS_PER_CHUNK", "8000"))
    OVERLAP_TOKENS = int(os.getenv("OVERLAP_TOKENS", "500"))
    CHUNK_OVERLAP_TOKENS = int(os.getenv("CHUNK_OVERLAP_TOKENS", "500"))
    
    # File Settings
    OUTPUT_DIRECTORY = Path(os.getenv("OUTPUT_DIRECTORY", "output"))
    SUPPORTED_FILE_TYPES = [".md", ".txt", ".rst"]
    MARKDOWN_EXTENSIONS = ['.md', '.markdown', '.mdown', '.mkdn', '.mkd']
    
    # Analysis Categories
    ANALYSIS_CATEGORIES = [
        "key_concepts",
        "evidence_and_examples", 
        "relationships",
        "insights",
        "questions_raised"
    ]
    
    # Logging Settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Output Settings
    MERMAID_THEME = os.getenv("MERMAID_THEME", "base")
    
    # MindMap Configuration
    MINDMAP_CONFIG = {
        "theme": "base",
        "orientation": "TB",
        "node_spacing": 20,
        "level_spacing": 40
    }
    
    @classmethod
    def get_model_configs(cls):
        """Get model configurations from web interface"""
        if SHARED_CONFIG_AVAILABLE:
            return SharedModelConfig.get_dynamic_model_configs()
        else:
            # Enhanced fallback with more models when web interface not available
            return {
                "gpt-5-mini": {
                    "max_tokens": 150000,
                    "cost_per_1k_tokens": 0.48,
                    "chunk_size": 22000,
                    "description": "Small, fast GPT-5 – most affordable general model"
                },
                "gpt-5o": {
                    "max_tokens": 200000,
                    "cost_per_1k_tokens": 4.0,
                    "chunk_size": 25000,
                    "description": "GPT-5 omni model for most tasks"
                },
                "gpt-4.1": {
                    "max_tokens": 150000,
                    "cost_per_1k_tokens": 8.0,
                    "chunk_size": 22000,
                    "description": "Latest GPT-4.1 model"
                },
                
                "o3-mini": {
                    "max_tokens": 200000,
                    "cost_per_1k_tokens": 5.0,
                    "chunk_size": 25000,
                    "description": "O3 mini reasoning model"
                }
            }
    
    @classmethod
    def get_available_models(cls):
        """Get list of available model names"""
        return list(cls.get_model_configs().keys())
    
    @classmethod
    def is_model_supported(cls, model_name):
        """Check if a model is supported"""
        return model_name in cls.get_model_configs()
    
    @classmethod
    def get_model_config(cls, model_name):
        """Get configuration for a specific model"""
        configs = cls.get_model_configs()
        return configs.get(model_name, {})

# Create instance for backward compatibility
config = Config()
