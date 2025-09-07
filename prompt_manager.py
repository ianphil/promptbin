import json
import os
import re
import sys
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
    WILDCARD_PATTERNS = ['*', '**']
    
    def __init__(self, data_dir: Optional[str] = None):
        """Initialize the PromptManager and ensure directories exist"""
        self.PROMPTS_DIR = Path(data_dir) if data_dir else Path(os.path.expanduser('~/promptbin-data'))
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        try:
            # First ensure the main data directory exists
            self.PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured main data directory exists: {self.PROMPTS_DIR}")
            
            for category in self.VALID_CATEGORIES:
                category_dir = self.PROMPTS_DIR / category
                category_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Ensured directory exists: {category_dir}")
        except PermissionError as e:
            error_msg = f"Permission denied creating directories at {self.PROMPTS_DIR}: {e}"
            logger.error(error_msg)
            logger.error("This may be due to a read-only file system. Consider using a writable directory like ~/promptbin-data")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error creating directories at {self.PROMPTS_DIR}: {e}")
            sys.exit(1)
    
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
                            if prompt_data is not None:
                                prompts.append(prompt_data)
                            else:
                                logger.warning(f"Skipping invalid prompt data (None) in {json_file}")
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
        Search prompts by query string with highlighting support
        
        Args:
            query: Search query string (supports * wildcard)
            category: Optional category to search within
            
        Returns:
            List of matching prompt data dictionaries with search highlighting
        """
        if not query.strip():
            return self.list_prompts(category)
        
        try:
            all_prompts = self.list_prompts(category)
            matching_prompts = []
            
            query_lower = query.lower().strip()
            
            # Handle wildcard searches
            if query_lower in self.WILDCARD_PATTERNS:
                return all_prompts
            
            for prompt in all_prompts:
                prompt_copy = prompt.copy()
                match_info = self._find_search_matches(prompt_copy, query_lower)
                
                if match_info['has_matches']:
                    # Add search metadata
                    prompt_copy['_search_highlights'] = match_info
                    matching_prompts.append(prompt_copy)
            
            return matching_prompts
            
        except Exception as e:
            logger.error(f"Error searching prompts: {e}")
            return []
    
    def _find_search_matches(self, prompt: Dict[str, Any], query_lower: str) -> Dict[str, Any]:
        """Find and return search match information for highlighting"""
        match_info = {
            'has_matches': False,
            'title_snippet': '',
            'content_snippet': '',
            'description_snippet': '',
            'matched_tags': []
        }
        
        # Check title
        title = prompt.get('title', '')
        if title and query_lower in title.lower():
            match_info['has_matches'] = True
            snippet = self._create_highlight_snippet(title, query_lower)
            match_info['title_snippet'] = self.highlight_text(snippet, query_lower)
        
        # Check content
        content = prompt.get('content', '')
        if content and query_lower in content.lower():
            match_info['has_matches'] = True
            snippet = self._create_highlight_snippet(content, query_lower, max_length=200)
            match_info['content_snippet'] = self.highlight_text(snippet, query_lower)
        
        # Check description
        description = prompt.get('description', '')
        if description and query_lower in description.lower():
            match_info['has_matches'] = True
            snippet = self._create_highlight_snippet(description, query_lower)
            match_info['description_snippet'] = self.highlight_text(snippet, query_lower)
        
        # Check tags
        tags = prompt.get('tags', [])
        for tag in tags:
            if query_lower in tag.lower():
                match_info['has_matches'] = True
                match_info['matched_tags'].append(tag)
        
        return match_info
    
    def _create_highlight_snippet(self, text: str, query_lower: str, max_length: int = 150) -> str:
        """Create a text snippet with the search query highlighted"""
        if not text or not query_lower:
            return text[:max_length] + ('...' if len(text) > max_length else '')
        
        # Find the first match position (case insensitive)
        text_lower = text.lower()
        match_start = text_lower.find(query_lower)
        
        if match_start == -1:
            return text[:max_length] + ('...' if len(text) > max_length else '')
        
        # Calculate snippet bounds
        snippet_start = max(0, match_start - max_length // 3)
        snippet_end = min(len(text), snippet_start + max_length)
        
        # Adjust start if we're too close to the end
        if snippet_end - snippet_start < max_length:
            snippet_start = max(0, snippet_end - max_length)
        
        snippet = text[snippet_start:snippet_end]
        
        # Add ellipsis if needed
        if snippet_start > 0:
            snippet = '...' + snippet
        if snippet_end < len(text):
            snippet = snippet + '...'
        
        return snippet
    
    def highlight_text(self, text: str, query: str) -> str:
        """Apply highlighting markup to text for the given query (case insensitive)"""
        if not text or not query:
            return text
        
        # Escape special regex characters in query
        query_escaped = re.escape(query)
        # Create case-insensitive pattern
        pattern = re.compile(f'({query_escaped})', re.IGNORECASE)
        # Replace with highlighted version
        return pattern.sub(r'<mark class="search-highlight">\1</mark>', text)
    
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
                    if prompt is None:
                        logger.warning(f"Found None prompt in category {category} - possible data integrity issue")
                        continue
                    # Collect unique tags
                    stats['total_tags'].update(prompt.get('tags', []))
                    
                    # Track recent activity (last 10) - safely get required fields
                    if all(key in prompt for key in ['id', 'title', 'category', 'updated_at']):
                        stats['recent_activity'].append({
                            'id': prompt['id'],
                            'title': prompt['title'],
                            'category': prompt['category'],
                            'updated_at': prompt['updated_at']
                        })
            
            # Sort recent activity and limit to 10
            stats['recent_activity'] = sorted(
                stats['recent_activity'],
                key=lambda x: x['updated_at'], 
                reverse=True
            )[:10]
            
            stats['total_tags'] = len(stats['total_tags'])
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {'total_prompts': 0, 'by_category': {}, 'total_tags': 0, 'recent_activity': []}