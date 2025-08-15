"""
Configuration settings for the Mind Map Creator
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Try to import shared configuration
try:
    # Add parent directory to access shared config
    current_dir = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(current_dir))
    from shared_config import SharedModelConfig
    SHARED_CONFIG_AVAILABLE = True
except ImportError:
    SHARED_CONFIG_AVAILABLE = False
    print("Warning: Shared config not available, using fallback models")

class Config:
    """Configuration class for Mind Map Creator"""
    
    # API Settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-5-mini")
    
    # Processing Settings
    MAX_TOKENS_PER_CHUNK = int(os.getenv("MAX_TOKENS_PER_CHUNK", "8000"))
    OVERLAP_TOKENS = int(os.getenv("OVERLAP_TOKENS", "500"))
    CHUNK_OVERLAP_TOKENS = int(os.getenv("CHUNK_OVERLAP_TOKENS", "500"))  # Alias for consistency
    
    # File Settings
    OUTPUT_DIRECTORY = Path(os.getenv("OUTPUT_DIRECTORY", "output"))
    SUPPORTED_FILE_TYPES = [".md", ".txt", ".rst"]
    
    # Dynamic Model Configuration
    @classmethod
    def get_model_configs(cls) -> Dict[str, Dict[str, Any]]:
        """Get model configurations dynamically"""
        if SHARED_CONFIG_AVAILABLE:
            return SharedModelConfig.get_dynamic_model_configs()
        else:
            # Fallback model configurations
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
                    "description": "Affordable o3 reasoning model"
                }
            }
    
    # Legacy property for backward compatibility
    @classmethod
    def get_model_configs_legacy(cls) -> Dict[str, Dict[str, Any]]:
        """Legacy method name for backward compatibility"""
        return cls.get_model_configs()
    
    # For backward compatibility, expose as class attribute
    @property
    def MODEL_CONFIGS(self) -> Dict[str, Dict[str, Any]]:
        """Model configurations property for backward compatibility"""
        return self.get_model_configs()
    
    # Analysis Configuration
    ANALYSIS_CATEGORIES = [
        "key_concepts",
        "evidence_and_examples", 
        "relationships",
        "insights",
        "questions_raised"
    ]
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # File Processing
    MARKDOWN_EXTENSIONS = ['.md', '.markdown', '.mdown', '.mkdn', '.mkd']
    
    # Output Configuration
    MERMAID_THEME = os.getenv("MERMAID_THEME", "base")
    
    # Validation settings
    @classmethod
    def is_model_supported(cls, model_name: str) -> bool:
        """Check if a model is supported by the system"""
        return model_name in cls.get_model_configs()
    
    @classmethod
    def get_model_config(cls, model_name: str) -> Dict[str, Any]:
        """Get configuration for a specific model"""
        configs = cls.get_model_configs()
        return configs.get(model_name, {})
    
    @classmethod
    def get_available_models(cls) -> list:
        """Get list of available model names"""
        return list(cls.get_model_configs().keys())

# For backward compatibility, create a global instance
config = Config()
MODEL_CONFIGS = config.get_model_configs()
