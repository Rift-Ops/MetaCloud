"""
Video URL Manager - Handle complex, encrypted and external video links
Supports:
- Local files (stored in sandbox)
- External URLs (long, complex, encrypted)
- URL decryption/decoding
- URL mapping and aliasing
"""

import os
import sys
import json
import base64
import hashlib
import re
import traceback
from urllib.parse import quote, unquote, urlparse


def _log(ctx, error):
    """Log an error to stderr and errors_logs.txt without depending on helpers.
    Forwards to victim logs in debug mode via helpers.log_error if available."""
    try:
        import sys as _sys
        _sys.stderr.write(f"[video_manager.{ctx}] {error}\n{traceback.format_exc()}\n")
    except Exception:
        pass
    try:
        from helpers import log_error
        log_error(f"video_manager.{ctx}", error)
    except Exception:
        pass
from config import get_video_dir, TARGETS_DIR

class VideoURLManager:
    """Manages video URLs and their mappings"""
    
    def __init__(self, target_id):
        self.tid = target_id
        self.video_dir = get_video_dir(target_id)
        self.mapping_file = os.path.join(self.video_dir, ".url_mapping.json")
        self.mappings = self._load_mappings()
    
    def _load_mappings(self):
        """Load URL mappings from file"""
        if os.path.exists(self.mapping_file):
            try:
                with open(self.mapping_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                _log(f"_load_mappings[{self.tid}]", e)
                return {}
        return {}
    
    def _save_mappings(self):
        """Save URL mappings to file"""
        os.makedirs(self.video_dir, exist_ok=True)
        with open(self.mapping_file, 'w') as f:
            json.dump(self.mappings, f, indent=2)
    
    def create_video_id(self, input_url_or_filename):
        """Create a short unique ID for a video URL or filename"""
        # Generate hash for uniqueness
        hash_obj = hashlib.md5(input_url_or_filename.encode())
        short_hash = hash_obj.hexdigest()[:12]
        return f"vid_{short_hash}"
    
    def decode_url(self, encoded_url):
        """Decode various URL encoding formats"""
        try:
            # Try base64 decoding first
            if encoded_url.startswith("b64:"):
                return base64.b64decode(encoded_url[4:]).decode()

            # Try URL decoding
            decoded = unquote(encoded_url)
            if decoded != encoded_url:
                return decoded

            # Try base64 without prefix
            try:
                return base64.b64decode(encoded_url).decode()
            except Exception as e:
                _log("decode_url.b64_fallback", e)

            # Return original if no decoding worked
            return encoded_url
        except Exception as e:
            _log("decode_url", e)
            return encoded_url
    
    def is_external_url(self, url):
        """Check if URL is an external link"""
        try:
            parsed = urlparse(url)
            return parsed.scheme in ['http', 'https']
        except Exception as e:
            _log("is_external_url", e)
            return False
    
    def register_video(self, input_source):
        """
        Register a video from various sources
        Returns: (video_id, video_url, is_external)
        
        input_source can be:
        - Local filename: "video.mp4"
        - External URL: "https://example.com/video.mp4"
        - Encoded URL: "b64:..." or URL-encoded string
        """
        
        # Decode if necessary
        decoded_source = self.decode_url(input_source)
        
        # Check if it's an external URL
        if self.is_external_url(decoded_source):
            video_id = self.create_video_id(decoded_source)
            
            # Store mapping for external URL
            self.mappings[video_id] = {
                "type": "external",
                "original": input_source,
                "decoded": decoded_source,
                "created": str(__import__('datetime').datetime.now())
            }
            self._save_mappings()
            
            return video_id, decoded_source, True
        
        else:
            # It's a local filename
            video_id = self.create_video_id(decoded_source)
            
            # Store mapping for local file
            self.mappings[video_id] = {
                "type": "local",
                "filename": decoded_source,
                "created": str(__import__('datetime').datetime.now())
            }
            self._save_mappings()
            
            return video_id, decoded_source, False
    
    def get_video_url(self, video_id):
        """
        Get the actual video URL for a video_id
        Returns: (url, is_external, original_input)
        """
        if video_id not in self.mappings:
            return None, False, None
        
        mapping = self.mappings[video_id]
        
        if mapping["type"] == "external":
            # Return the decoded external URL
            return mapping.get("decoded"), True, mapping.get("original")
        else:
            # Return local file reference
            return mapping.get("filename"), False, mapping.get("filename")
    
    def normalize_video_reference(self, video_data):
        """
        Normalize video reference in publication data
        Converts any video input to a clean reference
        """
        if not video_data:
            return None
        
        video_id, video_url, is_external = self.register_video(video_data)
        
        return {
            "id": video_id,
            "url": video_url,
            "is_external": is_external,
            "input": video_data
        }
    
    def cleanup_stale_mappings(self, days=30):
        """Remove mappings older than specified days"""
        import datetime
        threshold = datetime.datetime.now() - datetime.timedelta(days=days)
        
        keys_to_remove = []
        for video_id, mapping in self.mappings.items():
            try:
                created = datetime.datetime.fromisoformat(mapping.get("created", ""))
                if created < threshold:
                    keys_to_remove.append(video_id)
            except Exception as e:
                _log(f"cleanup_stale_mappings[{video_id}]", e)
        
        for key in keys_to_remove:
            del self.mappings[key]
        
        if keys_to_remove:
            self._save_mappings()
        
        return len(keys_to_remove)


def create_video_route_url(target_id, video_id):
    """
    Create a route URL for video serving
    Handles both local and external videos transparently
    """
    return f"/video_route/{target_id}/{video_id}"
