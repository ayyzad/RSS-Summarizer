import json
import os
from datetime import datetime, timedelta
from logger import setup_logger

logger = setup_logger(__name__)

class ArticleCache:
    def __init__(self, cache_file='processed_articles.json'):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        
    def _load_cache(self):
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            return {}
    
    def _save_cache(self):
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f)
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def is_processed(self, article_url):
        return article_url in self.cache
    
    def add_article(self, article_url):
        self.cache[article_url] = datetime.now().isoformat()
        self._save_cache()
    
    def cleanup_old_entries(self, days=30):
        """Remove entries older than specified days"""
        cutoff = datetime.now() - timedelta(days=days)
        self.cache = {
            url: date for url, date in self.cache.items()
            if datetime.fromisoformat(date) > cutoff
        }
        self._save_cache()