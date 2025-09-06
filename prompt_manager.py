import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptManager:
    """File-based storage manager for prompts"""
    
    VALID_CATEGORIES = ['coding', 'writing', 'analysis']
    PROMPTS_DIR = Path('prompts')
    
    def __init__(self):
        """Initialize the PromptManager and ensure directories exist"""
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        try:
            for category in self.VALID_CATEGORIES:
                category_dir = self.PROMPTS_DIR / category
                category_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Ensured directory exists: {category_dir}")
        except Exception as e:
            logger.error(f"Error creating directories: {e}")
            raise
    
    def _generate_unique_id(self) -> str:
        """Generate a unique ID for a new prompt"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = str(uuid.uuid4())[:8]
        return f"{timestamp}_{random_suffix}"
    
    def _validate_category(self, category: str) -> None:
        """Validate that category is allowed"""
        if category not in self.VALID_CATEGORIES:
            raise ValueError(f"Invalid category '{category}'. Must be one of: {self.VALID_CATEGORIES}")
    
    def _validate_prompt_data(self, data: Dict[str, Any]) -> None:
        """Validate prompt data structure"""
        required_fields = ['title', 'content', 'category']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        self._validate_category(data['category'])
        
        # Ensure title is not empty string
        if not data['title'].strip():
            raise ValueError("Title cannot be empty")
    
    def _get_prompt_path(self, prompt_id: str, category: str) -> Path:
        """Get the file path for a prompt"""
        return self.PROMPTS_DIR / category / f"{prompt_id}.json"
    
    def _find_prompt_file(self, prompt_id: str) -> Optional[Path]:
        """Find a prompt file by ID across all categories"""
        for category in self.VALID_CATEGORIES:
            prompt_path = self._get_prompt_path(prompt_id, category)
            if prompt_path.exists():
                return prompt_path
        return None
    
    def save_prompt(self, data: Dict[str, Any], prompt_id: Optional[str] = None) -> str:
        """
        Save a prompt to file storage
        
        Args:
            data: Prompt data dictionary
            prompt_id: Optional existing prompt ID for updates
            
        Returns:
            The prompt ID
        """
        try:
            # Validate input data
            self._validate_prompt_data(data)
            
            # Generate ID if creating new prompt
            if prompt_id is None:
                prompt_id = self._generate_unique_id()
                is_new = True
            else:
                is_new = False
            
            # Prepare prompt data
            now = datetime.now().isoformat()
            
            # If updating existing prompt, preserve created_at
            if not is_new:
                existing_prompt = self.get_prompt(prompt_id)
                created_at = existing_prompt.get('created_at', now) if existing_prompt else now
            else:
                created_at = now
            
            prompt_data = {
                'id': prompt_id,
                'title': data['title'].strip(),
                'content': data['content'],
                'category': data['category'],
                'description': data.get('description', '').strip(),
                'tags': [tag.strip() for tag in data.get('tags', '').split(',') if tag.strip()],
                'created_at': created_at,
                'updated_at': now
            }
            
            # Handle category change for existing prompts
            if not is_new:
                old_path = self._find_prompt_file(prompt_id)
                if old_path:
                    old_category = old_path.parent.name
                    if old_category != data['category']:
                        # Remove old file when category changes
                        old_path.unlink()
                        logger.info(f"Moved prompt {prompt_id} from {old_category} to {data['category']}")
            
            # Write to new location
            prompt_path = self._get_prompt_path(prompt_id, data['category'])
            
            with open(prompt_path, 'w', encoding='utf-8') as f:
                json.dump(prompt_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"{'Created' if is_new else 'Updated'} prompt {prompt_id}")
            return prompt_id
            
        except Exception as e:
            logger.error(f"Error saving prompt: {e}")
            raise
    
    def get_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a prompt by ID
        
        Args:
            prompt_id: The prompt ID to retrieve
            
        Returns:
            Prompt data dictionary or None if not found
        """
        try:
            prompt_path = self._find_prompt_file(prompt_id)
            if not prompt_path:
                return None
            
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Error retrieving prompt {prompt_id}: {e}")
            return None
    
    def list_prompts(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all prompts, optionally filtered by category
        
        Args:
            category: Optional category to filter by
            
        Returns:
            List of prompt data dictionaries
        """
        prompts = []
        
        try:
            categories = [category] if category else self.VALID_CATEGORIES
            
            for cat in categories:
                if category and cat != category:
                    continue
                    
                self._validate_category(cat)
                category_dir = self.PROMPTS_DIR / cat
                
                if not category_dir.exists():
                    continue
                
                for json_file in category_dir.glob('*.json'):
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            prompt_data = json.load(f)
                            prompts.append(prompt_data)
                    except Exception as e:
                        logger.error(f"Error reading prompt file {json_file}: {e}")
                        continue
            
            # Sort by updated_at (most recent first)
            prompts.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            
            return prompts
            
        except Exception as e:
            logger.error(f"Error listing prompts: {e}")
            return []
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """
        Delete a prompt by ID
        
        Args:
            prompt_id: The prompt ID to delete
            
        Returns:
            True if deleted successfully, False if not found
        """
        try:
            prompt_path = self._find_prompt_file(prompt_id)
            if not prompt_path:
                return False
            
            prompt_path.unlink()
            logger.info(f"Deleted prompt {prompt_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting prompt {prompt_id}: {e}")
            return False
    
    def search_prompts(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search prompts by query string
        
        Args:
            query: Search query string
            category: Optional category to search within
            
        Returns:
            List of matching prompt data dictionaries
        """
        if not query.strip():
            return self.list_prompts(category)
        
        try:
            all_prompts = self.list_prompts(category)
            matching_prompts = []
            
            query_lower = query.lower()
            
            for prompt in all_prompts:
                # Search in title, content, description, and tags
                searchable_text = ' '.join([
                    prompt.get('title', ''),
                    prompt.get('content', ''),
                    prompt.get('description', ''),
                    ' '.join(prompt.get('tags', []))
                ]).lower()
                
                if query_lower in searchable_text:
                    matching_prompts.append(prompt)
            
            return matching_prompts
            
        except Exception as e:
            logger.error(f"Error searching prompts: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about stored prompts"""
        try:
            stats = {
                'total_prompts': 0,
                'by_category': {},
                'total_tags': set(),
                'recent_activity': []
            }
            
            for category in self.VALID_CATEGORIES:
                prompts = self.list_prompts(category)
                stats['by_category'][category] = len(prompts)
                stats['total_prompts'] += len(prompts)
                
                for prompt in prompts:
                    # Collect unique tags
                    stats['total_tags'].update(prompt.get('tags', []))
                    
                    # Track recent activity (last 10)
                    stats['recent_activity'].append({
                        'id': prompt['id'],
                        'title': prompt['title'],
                        'category': prompt['category'],
                        'updated_at': prompt['updated_at']
                    })
            
            # Sort recent activity and limit to 10
            stats['recent_activity'].sort(
                key=lambda x: x['updated_at'], 
                reverse=True
            )[:10]
            
            stats['total_tags'] = len(stats['total_tags'])
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {'total_prompts': 0, 'by_category': {}, 'total_tags': 0, 'recent_activity': []}