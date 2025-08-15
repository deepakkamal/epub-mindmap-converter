#!/usr/bin/env python3
"""
Shared Configuration for EPUB to Mindmap System

This module provides unified model configuration for both the web interface
and the mindmap creator, eliminating hardcoded model restrictions.
"""

import os
import sys
from pathlib import Path

# Python version compatibility for typing
try:
    from typing import Dict, Any, List, Optional
except ImportError:
    # Fallback for older Python versions
    Dict = dict
    Any = object
    List = list
    Optional = object

# Add pricing manager to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from pricing_manager import get_pricing_summary, get_available_models
    PRICING_MANAGER_AVAILABLE = True
except ImportError:
    PRICING_MANAGER_AVAILABLE = False
    print("Warning: Pricing manager not available, using fallback models")

class SharedModelConfig:
    """Shared model configuration for the entire system"""
    
    # Default model configurations for cases where pricing manager is unavailable
    FALLBACK_MODEL_CONFIGS = {
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
        "gpt-5": {
            "max_tokens": 200000,
            "cost_per_1k_tokens": 8.0,
            "chunk_size": 25000,
            "description": "High-intelligence GPT-5 model"
        },
        "gpt-4o-mini": {
            "max_tokens": 128000,
            "cost_per_1k_tokens": 0.6,
            "chunk_size": 20000,
            "description": "Fastest and most affordable model in the GPT-4 family"
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
    
    @classmethod
    def get_dynamic_model_configs(cls) -> Dict[str, Dict[str, Any]]:
        """Get model configurations from pricing manager"""
        if not PRICING_MANAGER_AVAILABLE:
            return cls.FALLBACK_MODEL_CONFIGS
            
        try:
            pricing_data = get_pricing_summary()
            model_configs = {}
            
            for model_info in pricing_data.get('models', []):
                model_id = model_info['id']
                
                # Determine appropriate settings based on model type
                max_tokens, chunk_size = cls._get_model_specs(model_id)
                
                model_configs[model_id] = {
                    "max_tokens": max_tokens,
                    "cost_per_1k_tokens": model_info['output_cost'],
                    "chunk_size": chunk_size,
                    "description": model_info.get('description', 'AI language model'),
                    "name": model_info.get('name', model_id),
                    "input_cost": model_info.get('input_cost', 0),
                    "available_via_api": model_info.get('available_via_api', True)
                }
            
            return model_configs
            
        except Exception as e:
            print(f"Error loading dynamic models: {e}, using fallback")
            return cls.FALLBACK_MODEL_CONFIGS
    
    @classmethod
    def _get_model_specs(cls, model_id: str) -> tuple[int, int]:
        """Get max_tokens and chunk_size based on model type"""
        model_lower = model_id.lower()
        
        # O3 reasoning models
        if 'o3' in model_lower:
            return 200000, 25000
            
        # GPT-5 series
        if 'gpt-5' in model_lower:
            return 200000, 25000
            
        # GPT-4.1 series
        if 'gpt-4.1' in model_lower:
            return 150000, 22000
            
        # GPT-4o series
        if 'gpt-4o' in model_lower:
            return 128000, 20000
            
        # GPT-4 series
        if 'gpt-4' in model_lower:
            if 'turbo' in model_lower or 'preview' in model_lower:
                return 128000, 20000
            return 8000, 6000
            
        # Claude series
        if 'claude' in model_lower:
            return 200000, 25000
            
        # Default for unknown models
        return 128000, 20000
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """Get list of available model IDs"""
        return list(cls.get_dynamic_model_configs().keys())
    
    @classmethod
    def get_model_config(cls, model_id: str) -> Dict[str, Any]:
        """Get configuration for a specific model"""
        configs = cls.get_dynamic_model_configs()
        return configs.get(model_id, configs.get('gpt-4o-mini', cls.FALLBACK_MODEL_CONFIGS['gpt-4o-mini']))
    
    @classmethod
    def is_model_available(cls, model_id: str) -> bool:
        """Check if a model is available"""
        return model_id in cls.get_available_models()
    
    @classmethod
    def get_models_for_web_interface(cls) -> List[Dict[str, Any]]:
        """Get models formatted for web interface"""
        if not PRICING_MANAGER_AVAILABLE:
            return [
                {
                    'id': model_id,
                    'name': config.get('description', model_id),
                    'output_price': config['cost_per_1k_tokens'],
                    'description': config.get('description', 'AI language model')
                }
                for model_id, config in cls.FALLBACK_MODEL_CONFIGS.items()
            ]
        
        try:
            pricing_data = get_pricing_summary()
            return pricing_data.get('models', [])
        except Exception:
            return []

# Global instance
shared_config = SharedModelConfig()
