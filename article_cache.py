import os
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ArticleCache:
    def __init__(self, 
                 cache_file='articles/processed/processed_articles.json', 
                 archive_file='articles/processed/archived_processed_articles.json'):
        # Get project root directory (where main.py is located)
        project_root = Path(__file__).parent.parent
        
        # Create full paths relative to project root
        self.cache_file = project_root / cache_file
        self.archive_file = project_root / archive_file
        
        # Create directories if they don't exist
        os.makedirs(self.cache_file.parent, exist_ok=True)
        os.makedirs(self.archive_file.parent, exist_ok=True)
        
        self.cache = self._load_cache(self.cache_file)
        self.archive = self._load_cache(self.archive_file)
        self.cached_articles = set(self.cache.keys()) | set(self.archive.keys())
        
        # Debug logging
        logger.info(f"Loaded {len(self.cached_articles)} cached articles")
        logger.info(f"Cache file location: {self.cache_file}")
        logger.debug(f"First few cached URLs: {list(self.cached_articles)[:5]}")

    def _load_cache(self, filename):
        """Load cache from file, creating it if it doesn't exist"""
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_cache(self, data, filename):
        """Save cache to file with pretty formatting"""
        with open(filename, 'w') as f:
            json.dump(
                data,
                f,
                indent=2,
                sort_keys=True
            )

    def add_article(self, article_link):
        """Add article to cache and cached_articles set"""
        now = datetime.now().isoformat()
        self.cache[article_link] = now
        self.cached_articles.add(article_link)
        self._save_cache(self.cache, self.cache_file)
        logger.info(f"Added new article to cache: {article_link}")

    def is_processed(self, url):
        """Check if an article URL has been processed (in either cache or archive)"""
        return url in self.cache or url in self.archive

    def archive_old_entries(self, days=30):
        """Move entries older than specified days to archive"""
        cutoff = datetime.now() - timedelta(days=days)
        entries_to_archive = {}
        current_entries = {}

        # Separate entries into current and to-be-archived
        for url, processed_date in self.cache.items():
            if datetime.fromisoformat(processed_date) < cutoff:
                entries_to_archive[url] = processed_date
            else:
                current_entries[url] = processed_date

        # Update archive with new old entries
        self.archive.update(entries_to_archive)
        
        # Update cache to only contain current entries
        self.cache = current_entries

        # Save both files
        self._save_cache(self.cache, self.cache_file)
        self._save_cache(self.archive, self.archive_file)
        
        return len(entries_to_archive)

    def is_cached(self, article_link):
        """Check if an article URL has been processed"""
        is_cached = article_link in self.cached_articles
        if is_cached:
            logger.info(f"Found cached article: {article_link}")
        else:
            logger.debug(f"New article found: {article_link}")
        return is_cached