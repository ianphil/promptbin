"""
Share Manager for PromptBin
Handles creation and validation of shareable prompt links
"""

import os
import json
import secrets
import time
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta


class ShareManager:
    """Manages share tokens for prompts"""
    
    def __init__(self, share_file: str = "data/shares.json"):
        self.share_file = share_file
        self.shares: Dict[str, Dict[str, Any]] = {}
        self._ensure_data_dir()
        self._load_shares()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs(os.path.dirname(self.share_file), exist_ok=True)
    
    def _load_shares(self):
        """Load existing shares from file"""
        if os.path.exists(self.share_file):
            try:
                with open(self.share_file, 'r') as f:
                    self.shares = json.load(f)
                # Clean up expired shares on load
                self._cleanup_expired()
            except (json.JSONDecodeError, IOError):
                self.shares = {}
    
    def _save_shares(self):
        """Save shares to file"""
        try:
            with open(self.share_file, 'w') as f:
                json.dump(self.shares, f, indent=2)
        except IOError:
            pass  # Fail silently for now
    
    def _cleanup_expired(self):
        """Remove expired shares"""
        current_time = time.time()
        expired_tokens = [
            token for token, data in self.shares.items()
            if data.get('expires_at') and data['expires_at'] < current_time
        ]
        
        for token in expired_tokens:
            del self.shares[token]
        
        if expired_tokens:
            self._save_shares()
    
    def create_share_token(self, prompt_id: str, expires_in_hours: Optional[int] = None) -> str:
        """
        Create a new share token for a prompt
        
        Args:
            prompt_id: ID of the prompt to share
            expires_in_hours: Optional expiration in hours (None = never expires)
            
        Returns:
            Secure share token string
        """
        # Generate cryptographically secure token
        token = secrets.token_urlsafe(32)
        
        # Calculate expiration timestamp if specified
        expires_at = None
        if expires_in_hours is not None:
            expires_at = time.time() + (expires_in_hours * 3600)
        
        # Store share data
        self.shares[token] = {
            'prompt_id': prompt_id,
            'created_at': time.time(),
            'expires_at': expires_at,
            'access_count': 0
        }
        
        self._save_shares()
        return token
    
    def validate_share_token(self, token: str) -> Optional[str]:
        """
        Validate a share token and return prompt_id if valid
        
        Args:
            token: Share token to validate
            
        Returns:
            prompt_id if token is valid, None otherwise
        """
        if token not in self.shares:
            return None
        
        share_data = self.shares[token]
        
        # Check if token has expired
        if share_data.get('expires_at') and share_data['expires_at'] < time.time():
            # Remove expired token
            del self.shares[token]
            self._save_shares()
            return None
        
        # Increment access count
        share_data['access_count'] += 1
        self._save_shares()
        
        return share_data['prompt_id']
    
    def get_share_info(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a share token
        
        Args:
            token: Share token
            
        Returns:
            Share data dictionary or None if token doesn't exist
        """
        if token not in self.shares:
            return None
        
        share_data = self.shares[token].copy()
        
        # Convert timestamps to readable format
        if 'created_at' in share_data:
            share_data['created_at_readable'] = datetime.fromtimestamp(
                share_data['created_at']
            ).isoformat()
        
        if share_data.get('expires_at'):
            share_data['expires_at_readable'] = datetime.fromtimestamp(
                share_data['expires_at']
            ).isoformat()
            share_data['is_expired'] = share_data['expires_at'] < time.time()
        else:
            share_data['is_expired'] = False
        
        return share_data
    
    def revoke_share_token(self, token: str) -> bool:
        """
        Revoke a share token
        
        Args:
            token: Share token to revoke
            
        Returns:
            True if token was revoked, False if it didn't exist
        """
        if token in self.shares:
            del self.shares[token]
            self._save_shares()
            return True
        return False
    
    def list_shares_for_prompt(self, prompt_id: str) -> List[Dict[str, Any]]:
        """
        List all share tokens for a specific prompt
        
        Args:
            prompt_id: ID of the prompt
            
        Returns:
            List of share data dictionaries
        """
        shares = []
        for token, data in self.shares.items():
            if data['prompt_id'] == prompt_id:
                share_info = self.get_share_info(token)
                if share_info:  # Skip expired shares
                    share_info['token'] = token
                    shares.append(share_info)
        
        return sorted(shares, key=lambda x: x['created_at'], reverse=True)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get sharing statistics
        
        Returns:
            Dictionary with sharing stats
        """
        self._cleanup_expired()
        
        total_shares = len(self.shares)
        total_access_count = sum(data['access_count'] for data in self.shares.values())
        
        # Count shares by prompt
        prompt_shares = {}
        for data in self.shares.values():
            prompt_id = data['prompt_id']
            prompt_shares[prompt_id] = prompt_shares.get(prompt_id, 0) + 1
        
        return {
            'total_shares': total_shares,
            'total_access_count': total_access_count,
            'unique_prompts_shared': len(prompt_shares),
            'most_shared_prompts': sorted(
                prompt_shares.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
        }