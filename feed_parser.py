import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from config import MAX_ARTICLES, TIME_WINDOW
from logger import setup_logger
import logging

logger = setup_logger(__name__)

class FeedParser:
    def __init__(self, feed_url):
        self.feed_url = feed_url
        logger.setLevel(logging.INFO)
        logger.info(f"Initialized FeedParser for {feed_url}")

    def parse_feed(self):
        logger.info(f"Starting to parse feed: {self.feed_url}")
        feed = feedparser.parse(self.feed_url)
        articles = []
        cutoff_time = datetime.now() - timedelta(seconds=TIME_WINDOW)

        if hasattr(feed, 'status') and feed.status != 200:
            logger.error(f"Failed to fetch feed: {self.feed_url}, status: {feed.status}")
            return articles

        logger.info(f"Found {len(feed.entries)} entries in feed")
        
        for entry in feed.entries[:MAX_ARTICLES]:
            try:
                # Get publication date
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_date = datetime(*entry.updated_parsed[:6])
                else:
                    pub_date = datetime.now()  # Use current time if no date available
                
                # Extract article text
                article_text = self._extract_article_text(entry.link)
                
                if article_text:  # Only add if we successfully got the text
                    articles.append({
                        'title': entry.title,
                        'link': entry.link,
                        'text': article_text,
                        'published': pub_date
                    })
                    logger.info(f"Successfully extracted article: {entry.title}")
                
            except Exception as e:
                logger.error(f"Error processing entry: {str(e)}")

        logger.info(f"Successfully parsed {len(articles)} articles from feed")
        return articles

    def _extract_article_text(self, url):
        logger.debug(f"Extracting text from: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
                tag.decompose()
            
            paragraphs = soup.find_all('p')
            text = ' '.join(p.get_text().strip() for p in paragraphs)
            
            return text
        except Exception as e:
            logger.error(f"Error extracting text from {url}: {str(e)}")
            return None