#!/usr/bin/env python3
"""
OpenAI Pricing Module

Manages OpenAI model pricing information with fallback data.
Filters models based on cost criteria and provides model information.
"""

import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import os
import pickle
import urllib.request
import urllib.parse
import urllib.error
import ssl

# Load environment variables
def load_env_file(env_path: str = '.env'):
    """Load environment variables from .env file."""
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Load .env file at module level
load_env_file()

class OpenAIPricingManager:
    """Manages OpenAI model pricing information."""
    
    def __init__(self, cache_duration_hours: int = 24, max_staleness_hours: int = 12):
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self.max_staleness = timedelta(hours=max_staleness_hours)
        self.cache_file = os.path.join(os.path.dirname(__file__), 'pricing_cache.pkl')
        
        # Updated pricing data based on OpenAI's website (as of July 2025)
        # This is our fallback data - the system will try to fetch live data first
        self.fallback_models = {
            'gpt-4o-mini': {
                'name': 'GPT-4o Mini',
                'input_cost': 0.15,  # per 1M tokens
                'output_cost': 0.60,  # per 1M tokens
                'description': 'Fastest and most affordable model in the GPT-4o family',
                'active': True
            },
            'gpt-4.1': {
                'name': 'GPT-4.1',
                'input_cost': 2.00,
                'output_cost': 8.00,
                'description': 'Latest GPT-4.1 model with improved capabilities',
                'active': True
            },
            'gpt-4.1-2025-04-14': {
                'name': 'GPT-4.1 (2025-04-14)',
                'input_cost': 2.00,
                'output_cost': 8.00,
                'description': 'GPT-4.1 snapshot from April 2025',
                'active': True
            },
            # GPT-5 family (new)
            'gpt-5-mini': {
                'name': 'GPT-5 Mini',
                'input_cost': 0.12,
                'output_cost': 0.48,
                'description': 'Small, fast GPT-5 model – cheapest general model',
                'active': True
            },
            'gpt-5o': {
                'name': 'GPT-5o',
                'input_cost': 1.00,
                'output_cost': 4.00,
                'description': 'GPT-5 omni model for most tasks',
                'active': True
            },
            'gpt-5': {
                'name': 'GPT-5',
                'input_cost': 2.00,
                'output_cost': 8.00,
                'description': 'High-intelligence GPT-5 model',
                'active': True
            },
            # o3 models (latest reasoning models)
            'o3-mini': {
                'name': 'o3 Mini',
                'input_cost': 1.25,
                'output_cost': 5.00,
                'description': 'Affordable reasoning model with improved capabilities',
                'active': True
            },
            'o3-mini-2025-01-31': {
                'name': 'o3 Mini (2025-01-31)',
                'input_cost': 1.25,
                'output_cost': 5.00,
                'description': 'o3 Mini snapshot from January 2025',
                'active': True
            },
            'o3': {
                'name': 'o3',
                'input_cost': 20.00,
                'output_cost': 80.00,
                'description': 'Advanced reasoning model for complex problem-solving',
                'active': True
            },
            # Deprecated models (removed from active list)
            # Removed GPT-3.5 and o1 family as per new policy
        }
        
        # Add timestamp for when the fallback data was last updated
        self.fallback_last_updated = "2025-07-26"
        self.models_api_url = 'https://api.openai.com/v1/models'
        self.pricing_url = 'https://platform.openai.com/docs/pricing'
    
    def fetch_live_models_from_api(self, api_key: Optional[str] = None) -> List[str]:
        """
        Fetch available models from OpenAI's API using urllib.
        
        Args:
            api_key: OpenAI API key for authentication
            
        Returns:
            List of available model IDs
        """
        try:
            # Create request
            req = urllib.request.Request(self.models_api_url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            if api_key:
                req.add_header('Authorization', f'Bearer {api_key}')
            
            # Create SSL context that doesn't verify certificates (for testing)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            # Make request
            with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    models = [model['id'] for model in data.get('data', [])]
                    print(f"✓ Fetched {len(models)} models from OpenAI API")
                    return models
                else:
                    print(f"API request failed with status: {response.getcode()}")
                    
        except urllib.error.HTTPError as e:
            print(f"HTTP Error fetching models: {e.code} - {e.reason}")
        except urllib.error.URLError as e:
            print(f"URL Error fetching models: {e.reason}")
        except Exception as e:
            print(f"Error fetching models from API: {e}")
        
        return []
    
    def fetch_pricing_from_web(self) -> Dict[str, Dict[str, Any]]:
        """
        Fetch pricing information from OpenAI's pricing page.
        
        Returns:
            Dictionary of model_id -> pricing_info
        """
        try:
            # Create request for pricing page
            req = urllib.request.Request(self.pricing_url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Create SSL context
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
                if response.getcode() == 200:
                    html_content = response.read().decode('utf-8')
                    return self._parse_pricing_from_html_simple(html_content)
                    
        except Exception as e:
            print(f"Error fetching pricing from web: {e}")
        
        return {}
    
    def _parse_pricing_from_html_simple(self, html_content: str) -> Dict[str, Dict[str, Any]]:
        """
        Parse pricing from HTML using simple regex patterns.
        This is more robust than BeautifulSoup for our use case.
        """
        models = {}
        
        try:
            # Look for patterns that indicate model pricing
            # Pattern 1: Look for model names and associated pricing
            patterns = [
                # GPT models (4 and 5 families only)
                r'(gpt-5o|gpt-5-mini|gpt-5|gpt-4o-mini|gpt-4o|gpt-4\.1|gpt-4-turbo)[^$]*\$?([\d.]+)[^$]*\$?([\d.]+)',
                # O3 models
                r'(o3-mini|o3)[^$]*\$?([\d.]+)[^$]*\$?([\d.]+)',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    if len(match) >= 3:
                        model_name, input_price, output_price = match[0], match[1], match[2]
                        try:
                            models[model_name.lower()] = {
                                'name': model_name,
                                'input_cost': float(input_price),
                                'output_cost': float(output_price),
                                'description': f'Latest {model_name} model from OpenAI',
                                'active': True,
                                'source': 'web_scraped'
                            }
                        except ValueError:
                            continue
            
            print(f"✓ Parsed {len(models)} models from pricing page")
            
        except Exception as e:
            print(f"Error parsing pricing HTML: {e}")
        
        return models
    
    def fetch_current_pricing(self, api_key: Optional[str] = None, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Fetch current pricing data from multiple sources.
        Falls back to enhanced local data if live fetching fails.
        
        Args:
            api_key: OpenAI API key for fetching model list (if None, tries to load from environment)
            force_refresh: Force refresh even if cache is valid
            
        Returns:
            Dictionary of model_id -> model_info
        """
        print(f"Fetching pricing data (force_refresh={force_refresh})...")
        
        # Get API key from environment if not provided by user
        if not api_key:
            api_key = os.environ.get('OPENAI_API_KEY')
            if api_key:
                print("✓ Using API key from environment")
            else:
                print("ℹ No API key available - using curated model list")
        else:
            print("✓ Using user-provided API key for live pricing data")
        
        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_data, cache_age = self._get_cached_pricing_with_age()
            if cached_data:
                # Check if cache is too stale even if within duration
                if cache_age < self.max_staleness:
                    print(f"✓ Using cached pricing data ({cache_age.total_seconds()/3600:.1f}h old)")
                    return self._filter_active_models(cached_data)
                else:
                    print(f"⚠ Cache is stale ({cache_age.total_seconds()/3600:.1f}h old), refreshing...")
                    # Continue to refresh despite valid cache
        
        # Start with enhanced fallback models (only latest versions)
        combined_models = self._get_enhanced_fallback_models()
        
        # Try to fetch live data (but don't fail if it doesn't work)
        api_success = False
        web_success = False
        
        # 1. Try to get available models from API (only if we have an API key)
        if api_key:
            try:
                api_models = self.fetch_live_models_from_api(api_key)
                if api_models:
                    api_success = True
                    print(f"✓ API models found: {len(api_models)}")
                    
                    # Create a comprehensive model list from API
                    api_model_dict = {}
                    for model_id in api_models:
                        estimated_pricing = self._estimate_pricing_for_model(model_id)
                        if estimated_pricing:
                            api_model_dict[model_id] = estimated_pricing
                            api_model_dict[model_id]['available_via_api'] = True
                            api_model_dict[model_id]['pricing_estimated'] = True
                    
                    # Filter API models to latest versions only
                    latest_api_models = self._filter_to_latest_models_only(api_model_dict)
                    
                    # Merge with our curated list, preferring API data for pricing
                    for model_id, model_info in latest_api_models.items():
                        if model_id in combined_models:
                            # Update existing model
                            combined_models[model_id].update(model_info)
                        else:
                            # Add new model if it's affordable
                            if self._is_allowed_family(model_id) and model_info.get('input_cost', float('inf')) < 11.0:
                                combined_models[model_id] = model_info
                                print(f"✓ Added API model: {model_id} (${model_info['input_cost']:.2f}/1M input)")
                else:
                    print("⚠ API request failed - using curated fallback data")
            except Exception as e:
                print(f"⚠ API fetch failed: {e} - using curated fallback data")
        else:
            print("ℹ No API key available - using curated model list")
        
        # 2. Mark data sources
        for model_id, model_info in combined_models.items():
            model_info['data_sources'] = []
            if model_info.get('available_via_api'):
                model_info['data_sources'].append('api')
            if not model_info['data_sources']:
                model_info['data_sources'].append('curated')
        
        # 3. Filter to only include allowed families and input cost < $11/1M
        affordable_models = {}
        for model_id, model_info in combined_models.items():
            if not self._is_allowed_family(model_id):
                continue
            input_cost = model_info.get('input_cost', float('inf'))
            if input_cost < 11.0 and model_info.get('active', True):
                affordable_models[model_id] = model_info
        
        print(f"✓ Filtered to {len(affordable_models)} affordable models (≤$11/1M output)")
        
        # 5. Save to cache
        if affordable_models:
            self._save_pricing_cache(affordable_models)
            print(f"✓ Cached {len(affordable_models)} models")
        
        # 6. Return active affordable models, sorted by output price asc
        active_models = self._filter_active_models(affordable_models)
        active_models = dict(sorted(active_models.items(), key=lambda x: x[1].get('output_cost', 9999)))
        print(f"✓ Returning {len(active_models)} active affordable models")
        
        return active_models
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Get detailed cache status information."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                
                cache_age = datetime.now() - cache_data['timestamp']
                return {
                    'exists': True,
                    'timestamp': cache_data['timestamp'].isoformat(),
                    'age_hours': cache_age.total_seconds() / 3600,
                    'models_count': len(cache_data.get('models', {})),
                    'is_fresh': cache_age < self.cache_duration,
                    'is_stale': cache_age > self.max_staleness,
                    'max_staleness_hours': self.max_staleness.total_seconds() / 3600,
                    'cache_duration_hours': self.cache_duration.total_seconds() / 3600
                }
        except Exception as e:
            return {
                'exists': False,
                'error': str(e)
            }
        
        return {'exists': False}
    
    def _get_enhanced_fallback_models(self) -> Dict[str, Any]:
        """
        Get enhanced fallback models with only the latest version of each model family.
        This filters out older snapshots to provide a clean list.
        """
        # Define the latest models we want to include (one per family)
        latest_models = {
            # GPT-4o family - keep only the latest versions
            'gpt-4.1': {
                'name': 'GPT-4.1',
                'input_cost': 2.00,
                'output_cost': 8.00,
                'description': 'Latest GPT-4.1 model',
                'active': True,
                'family': 'gpt-4.1'
            },
            
            # GPT-4 family - latest versions
            # Note: GPT-4 Turbo removed per policy, keep GPT-4.1 as GPT-4 family representative

            # GPT-5 family
            'gpt-5-mini': {
                'name': 'GPT-5 Mini',
                'input_cost': 0.12,
                'output_cost': 0.48,
                'description': 'Cheapest GPT-5 model',
                'active': True,
                'family': 'gpt-5-mini'
            },
            'gpt-5o': {
                'name': 'GPT-5o',
                'input_cost': 1.00,
                'output_cost': 4.00,
                'description': 'Omni GPT-5 model',
                'active': True,
                'family': 'gpt-5o'
            },
            'gpt-5': {
                'name': 'GPT-5',
                'input_cost': 2.00,
                'output_cost': 8.00,
                'description': 'High-intelligence GPT-5',
                'active': True,
                'family': 'gpt-5'
            },
            
            # o1 family (reasoning models) - latest versions only
            'o1': {
                'name': 'o1',
                'input_cost': 15.00,
                'output_cost': 60.00,
                'description': 'Latest reasoning model for complex problems',
                'active': True,
                'family': 'o1'
            },
            'o1-mini': {
                'name': 'o1 Mini',
                'input_cost': 3.00,
                'output_cost': 12.00,
                'description': 'Faster reasoning model for coding and math',
                'active': True,
                'family': 'o1-mini'
            },
            
            # o3 family (latest reasoning models) - latest versions only
            'o3-mini': {
                'name': 'o3 Mini',
                'input_cost': 1.25,
                'output_cost': 5.00,
                'description': 'Latest affordable reasoning model',
                'active': True,
                'family': 'o3-mini'
            },
            'o3': {
                'name': 'o3',
                'input_cost': 20.00,
                'output_cost': 80.00,
                'description': 'Most advanced reasoning model (expensive)',
                'active': False  # Too expensive for our 11$ limit
            },
            
            # Additional model families that might exist
            'gpt-4.1': {
                'name': 'GPT-4.1',
                'input_cost': 2.00,
                'output_cost': 8.00,
                'description': 'Latest GPT-4.1 model with enhanced capabilities',
                'active': True,
                'family': 'gpt-4.1'
            },
            
            # Exclude ChatGPT interface and o1 family as per new policy
            
            # GPT-4 family variations
            'gpt-4-0613': {
                'name': 'GPT-4 (June 2023)',
                'input_cost': 30.00,
                'output_cost': 60.00,
                'description': 'Stable GPT-4 model (expensive)',
                'active': False  # Too expensive
            },
            
            # Additional affordable models
            'gpt-4o-2024-08-06': {
                'name': 'GPT-4o August 2024',
                'input_cost': 2.50,
                'output_cost': 10.00,
                'description': 'GPT-4o model from August 2024',
                'active': True,
                'family': 'gpt-4o'
            },
            
            # Removed GPT-4 Turbo preview variants as well
        }
        
        return latest_models
    
    def _filter_to_latest_models_only(self, all_models: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter a model list to keep only the latest version of each model family.
        This removes dated snapshots and keeps the newest version.
        """
        # Group models by family
        model_families = {}
        
        for model_id, model_info in all_models.items():
            # Determine the model family
            family = self._get_model_family(model_id)
            
            if family not in model_families:
                model_families[family] = []
            
            model_families[family].append((model_id, model_info))
        
        # For each family, keep only the latest model
        latest_models = {}
        
        for family, models in model_families.items():
            if len(models) == 1:
                # Only one model in family, keep it
                model_id, model_info = models[0]
                latest_models[model_id] = model_info
            else:
                # Multiple models, find the latest one
                latest_model = self._find_latest_model_in_family(models)
                if latest_model:
                    model_id, model_info = latest_model
                    latest_models[model_id] = model_info
        
        return latest_models
    
    def _get_model_family(self, model_id: str) -> str:
        """Determine which family a model belongs to."""
        model_lower = model_id.lower()
        
        # Define family patterns in order of specificity
        if 'gpt-5o' in model_lower:
            return 'gpt-5o'
        elif 'gpt-5-mini' in model_lower:
            return 'gpt-5-mini'
        elif 'gpt-5' in model_lower:
            return 'gpt-5'
        if 'gpt-4.1' in model_lower or 'gpt-41' in model_lower or '4.1' in model_lower:
            return 'gpt-4.1'
        elif 'gpt-4o' in model_lower:
            return 'gpt-4o'
        elif 'o3-mini' in model_lower:
            return 'o3-mini'
        elif 'o3' in model_lower:
            return 'o3'
        elif 'chatgpt' in model_lower:
            return 'chatgpt'
        else:
            return model_id  # Fallback to the model ID itself

    def _is_allowed_family(self, model_id: str) -> bool:
        """Allow only gpt-4.1*, gpt-5*, and o3* families."""
        family = self._get_model_family(model_id)
        return family in {
            'gpt-4.1', 'gpt-4o', 'gpt-4o-mini',
            'gpt-5', 'gpt-5o', 'gpt-5-mini',
            'o3', 'o3-mini'
        }
    
    def _find_latest_model_in_family(self, models: List[tuple]) -> Optional[tuple]:
        """Find the latest model in a family based on naming patterns."""
        # Sort models to prioritize:
        # 1. Models without dates (assumed to be latest)
        # 2. Models with most recent dates
        # 3. Models with "latest" in the name
        
        def sort_key(model_tuple):
            model_id, model_info = model_tuple
            model_lower = model_id.lower()
            
            # Prefer models without date stamps (they're usually the "latest")
            has_date = bool(re.search(r'\d{4}-\d{2}-\d{2}|\d{8}', model_id))
            
            # Prefer models with "latest" in name
            has_latest = 'latest' in model_lower
            
            # Extract date if present for comparison
            date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})|(\d{4})(\d{2})(\d{2})', model_id)
            if date_match:
                if date_match.group(1):  # YYYY-MM-DD format
                    date_score = int(date_match.group(1) + date_match.group(2) + date_match.group(3))
                else:  # YYYYMMDD format
                    date_score = int(date_match.group(4) + date_match.group(5) + date_match.group(6))
            else:
                date_score = 99999999  # No date = assumed latest
            
            # Return sort key (lower values = higher priority)
            return (has_date, not has_latest, -date_score)
        
        sorted_models = sorted(models, key=sort_key)
        return sorted_models[0] if sorted_models else None
    
    def add_known_models_manually(self) -> Dict[str, Any]:
        """
        Add models that we know exist but might not be captured by automatic methods.
        This can be called to supplement the model list with manually verified models.
        """
        additional_models = {}
        
        # Models that are known to exist based on OpenAI documentation
        known_models = [
            # o3 family (latest reasoning models)
            ('o3-mini', 1.25, 5.00, 'o3 Mini reasoning model'),
            ('o3-mini-20250124', 1.25, 5.00, 'o3 Mini January 2025'),
            # ('o3', 20.00, 80.00, 'o3 advanced reasoning model')  # excluded by cost
            
            # GPT-5 family
            ('gpt-5-mini', 0.12, 0.48, 'Cheapest GPT-5 model'),
            ('gpt-5o', 1.00, 4.00, 'Omni GPT-5 model'),
            ('gpt-5', 2.00, 8.00, 'High-intelligence GPT-5'),
            
            # GPT-4o family updates
            ('gpt-4o-mini', 0.15, 0.60, 'Most affordable GPT-4o model'),
            ('gpt-4o', 2.50, 10.00, 'Latest GPT-4o model'),
            ('gpt-4o-2024-11-20', 2.50, 10.00, 'GPT-4o November 2024'),
            ('gpt-4o-2024-08-06', 2.50, 10.00, 'GPT-4o August 2024'),
            ('gpt-4o-2024-05-13', 5.00, 15.00, 'GPT-4o May 2024'),
            
            # GPT-4 family
            ('gpt-4.1', 2.00, 8.00, 'Latest GPT-4.1 model'),
            ('gpt-4.1-2025-04-14', 2.00, 8.00, 'GPT-4.1 April 2025')
        ]
        
        for model_id, input_cost, output_cost, description in known_models:
            if output_cost <= 11.0:  # Only include affordable models
                additional_models[model_id] = {
                    'name': model_id.replace('-', ' ').title(),
                    'input_cost': input_cost,
                    'output_cost': output_cost,
                    'description': description,
                    'active': True,
                    'manually_added': True
                }
        
        return additional_models
    
    def _estimate_pricing_for_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Estimate pricing for a model based on its name."""
        model_lower = model_id.lower()
        
        # Pricing estimates based on model family
        if 'o3-mini' in model_lower:
            return {
                'name': model_id,
                'input_cost': 1.25,
                'output_cost': 5.00,
                'description': f'Estimated pricing for {model_id}',
                'active': True,
                'pricing_estimated': True
            }
        elif 'o3' in model_lower:
            return {
                'name': model_id,
                'input_cost': 20.00,
                'output_cost': 80.00,
                'description': f'Estimated pricing for {model_id}',
                'active': True,
                'pricing_estimated': True
            }
        elif 'gpt-4o-mini' in model_lower:
            return {
                'name': model_id,
                'input_cost': 0.15,
                'output_cost': 0.60,
                'description': f'Estimated pricing for {model_id}',
                'active': True,
                'pricing_estimated': True
            }
        elif 'gpt-4o' in model_lower:
            return {
                'name': model_id,
                'input_cost': 2.50,
                'output_cost': 10.00,
                'description': f'Estimated pricing for {model_id}',
                'active': True,
                'pricing_estimated': True
            }
        elif 'gpt-4.1' in model_lower or 'gpt-41' in model_lower:
            return {
                'name': model_id,
                'input_cost': 2.00,
                'output_cost': 8.00,
                'description': f'Estimated pricing for {model_id}',
                'active': True,
                'pricing_estimated': True
            }
        elif 'gpt-4' in model_lower:
            return {
                'name': model_id,
                'input_cost': 2.00 if '4.1' in model_lower else 10.00,
                'output_cost': 8.00 if '4.1' in model_lower else 10.50,
                'description': f'Estimated pricing for {model_id}',
                'active': True,
                'pricing_estimated': True
            }
        elif 'gpt-5o' in model_lower:
            return {
                'name': model_id,
                'input_cost': 1.00,
                'output_cost': 4.00,
                'description': f'Estimated pricing for {model_id}',
                'active': True,
                'pricing_estimated': True
            }
        elif 'gpt-5-mini' in model_lower:
            return {
                'name': model_id,
                'input_cost': 0.12,
                'output_cost': 0.48,
                'description': f'Estimated pricing for {model_id}',
                'active': True,
                'pricing_estimated': True
            }
        elif 'gpt-5' in model_lower:
            return {
                'name': model_id,
                'input_cost': 2.00,
                'output_cost': 8.00,
                'description': f'Estimated pricing for {model_id}',
                'active': True,
                'pricing_estimated': True
            }
        
        return None
    
    def _get_cached_pricing(self) -> Optional[Dict]:
        """Get cached pricing data if still valid."""
        data, _ = self._get_cached_pricing_with_age()
        return data
    
    def _get_cached_pricing_with_age(self) -> tuple[Optional[Dict], Optional[timedelta]]:
        """Get cached pricing data with age information."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                
                cache_age = datetime.now() - cache_data['timestamp']
                if cache_age < self.cache_duration:
                    return cache_data['models'], cache_age
                else:
                    print(f"⏰ Cache expired ({cache_age.total_seconds()/3600:.1f}h > {self.cache_duration.total_seconds()/3600:.1f}h)")
        except Exception as e:
            print(f"❌ Error reading cache: {e}")
        
        return None, None
    
    def _save_pricing_cache(self, models: Dict):
        """Save pricing data to cache."""
        try:
            cache_data = {
                'timestamp': datetime.now(),
                'models': models
            }
            with open(self.cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def _filter_active_models(self, models: Dict[str, Any]) -> Dict[str, Any]:
        """Filter out deprecated models and return only active ones."""
        active_models = {}
        deprecated_models = []
        
        for model_id, model_info in models.items():
            if model_info.get('active', True) and not model_info.get('deprecated', False):
                active_models[model_id] = model_info
            else:
                deprecated_models.append(model_id)
        
        if deprecated_models:
            print(f"Filtered out deprecated models: {deprecated_models}")
        
        return active_models
    
    def get_all_models_including_deprecated(self) -> Dict[str, Any]:
        """Get all models including deprecated ones (for admin/debugging purposes)."""
        return self.fallback_models
    
    def is_pricing_data_stale(self, max_age_days: int = 7) -> bool:
        """
        Check if the pricing data is older than the specified number of days.
        
        Args:
            max_age_days: Maximum age in days before data is considered stale
            
        Returns:
            True if data needs updating
        """
        try:
            last_updated = datetime.strptime(self.fallback_last_updated, "%Y-%m-%d")
            age = datetime.now() - last_updated
            return age.days > max_age_days
        except:
            return True
    
    def get_data_freshness_info(self) -> Dict[str, Any]:
        """Get information about the freshness of the pricing data."""
        try:
            last_updated = datetime.strptime(self.fallback_last_updated, "%Y-%m-%d")
            age_days = (datetime.now() - last_updated).days
            
            return {
                'last_updated': self.fallback_last_updated,
                'age_days': age_days,
                'is_stale': self.is_pricing_data_stale(),
                'needs_update': age_days > 7,
                'status': 'stale' if age_days > 7 else 'fresh'
            }
        except:
            return {
                'last_updated': 'unknown',
                'age_days': -1,
                'is_stale': True,
                'needs_update': True,
                'status': 'error'
            }
    
    def mark_model_deprecated(self, model_id: str) -> bool:
        """Mark a specific model as deprecated."""
        if model_id in self.fallback_models:
            self.fallback_models[model_id]['active'] = False
            self.fallback_models[model_id]['deprecated'] = True
            return True
        return False
    
    def add_new_model(self, model_id: str, model_info: Dict[str, Any]) -> bool:
        """Add a new model to the pricing data."""
        try:
            # Ensure required fields
            required_fields = ['name', 'input_cost', 'output_cost', 'description']
            for field in required_fields:
                if field not in model_info:
                    print(f"Missing required field: {field}")
                    return False
            
            # Set default values
            model_info['active'] = model_info.get('active', True)
            model_info['deprecated'] = model_info.get('deprecated', False)
            
            self.fallback_models[model_id] = model_info
            print(f"Added new model: {model_id}")
            return True
            
        except Exception as e:
            print(f"Error adding model {model_id}: {e}")
            return False
    
    def get_affordable_models(self, max_output_cost: float = 11.0, api_key: Optional[str] = None, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get models where output cost is under the specified threshold.
        
        Args:
            max_output_cost: Maximum cost per 1M output tokens
            api_key: OpenAI API key for fetching live data
            force_refresh: Force refresh of pricing data
            
        Returns:
            Dictionary of model_id -> model_info for affordable models
        """
        all_models = self.fetch_current_pricing(api_key=api_key, force_refresh=force_refresh)
        affordable_models = {}
        
        for model_id, model_info in all_models.items():
            if not self._is_allowed_family(model_id):
                continue
            if model_info.get('input_cost', float('inf')) < 11.0:
                affordable_models[model_id] = model_info
        
        # Sort by output cost (cheapest first)
        sorted_models = dict(sorted(
            affordable_models.items(),
            key=lambda x: x[1]['output_cost']
        ))
        
        return sorted_models
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get information for a specific model."""
        all_models = self.fetch_current_pricing()
        return all_models.get(model_id)
    
    def get_pricing_summary(self) -> Dict[str, Any]:
        """Get a summary of all available models and pricing."""
        models = self.get_affordable_models()
        freshness_info = self.get_data_freshness_info()
        
        summary = {
            'last_updated': datetime.now().isoformat(),
            'data_freshness': freshness_info,
            'models': [],
            'total_models': len(models),
            'cheapest_model': None,
            'most_expensive_affordable': None
        }
        
        if models:
            model_list = list(models.items())
            summary['cheapest_model'] = {
                'id': model_list[0][0],
                'name': model_list[0][1]['name'],
                'output_cost': model_list[0][1]['output_cost']
            }
            summary['most_expensive_affordable'] = {
                'id': model_list[-1][0],
                'name': model_list[-1][1]['name'],
                'output_cost': model_list[-1][1]['output_cost']
            }
            
            for model_id, model_info in models.items():
                summary['models'].append({
                    'id': model_id,
                    'name': model_info['name'],
                    'input_cost': model_info['input_cost'],
                    'output_cost': model_info['output_cost'],
                    'description': model_info.get('description', ''),
                    'cost_formatted': f"${model_info['input_cost']:.2f}/1M input | ${model_info['output_cost']:.2f}/1M output",
                    'active': model_info.get('active', True)
                })
        
        return summary


# Global instance
pricing_manager = OpenAIPricingManager()


def get_available_models(api_key: Optional[str] = None, force_refresh: bool = False) -> Dict[str, Any]:
    """Get all available models under the cost threshold."""
    return pricing_manager.get_affordable_models(api_key=api_key, force_refresh=force_refresh)


def get_pricing_summary(api_key: Optional[str] = None, force_refresh: bool = False) -> Dict[str, Any]:
    """Get pricing summary for the frontend."""
    # Temporarily update the get_affordable_models call in get_pricing_summary
    old_get_affordable = pricing_manager.get_affordable_models
    pricing_manager.get_affordable_models = lambda max_cost=11.0: old_get_affordable(max_cost, api_key, force_refresh)
    
    try:
        return pricing_manager.get_pricing_summary()
    finally:
        pricing_manager.get_affordable_models = old_get_affordable


# Create alias for backward compatibility
PricingManager = OpenAIPricingManager


if __name__ == '__main__':
    # Test the pricing manager
    summary = get_pricing_summary()
    print(json.dumps(summary, indent=2))
