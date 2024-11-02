import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from config import MAX_ARTICLES, TIME_WINDOW
from logger import setup_logger
from dateutil import parser as date_parser

def parse_date(date_str):
    try:
        return date_parser.parse(date_str)
    except (ValueError, TypeError):
        return datetime.now()  # Default to current time if parsing fails

class FeedParser:
    def __init__(self, feed_url):
        self.feed_url = feed_url
        self.logger = setup_logger(__name__)
        self.logger.info(f"Initialized FeedParser for {feed_url}")

    def parse_feed(self):
        try:
            self.logger.info(f"Starting to parse feed: {self.feed_url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.feed_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                self.logger.error(f"Failed to fetch feed: {self.feed_url}, status: {response.status_code}")
                return []

            feed = feedparser.parse(response.text)
            entries = feed.entries[:MAX_ARTICLES]
            
            if not entries:
                self.logger.info(f"No entries found in feed")
                return []
            
            self.logger.info(f"Found {len(entries)} entries in feed")
            
            articles = []
            for entry in entries:
                article = self.extract_article_text(entry)
                if article:
                    articles.append(article)
            
            return articles
            
        except Exception as e:
            self.logger.error(f"Error parsing feed {self.feed_url}: {str(e)}")
            return []

    def extract_article_text(self, entry):
        try:
            title = entry.get('title', '')
            link = entry.get('link', '')
            
            # First try to get the full article content by visiting the URL
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(link, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Remove unwanted elements
                    for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer']):
                        element.decompose()
                    
                    # Try common article content selectors
                    article_content = None
                    selectors = [
                        'article', 
                        '.article-content',
                        '.post-content',
                        '.entry-content',
                        'main',
                        '#content'
                    ]
                    
                    for selector in selectors:
                        content = soup.select_one(selector)
                        if content:
                            article_content = content.get_text(separator=' ', strip=True)
                            break
                    
                    # If no content found with selectors, fall back to summary
                    text = article_content if article_content else entry.get('summary', '')
                else:
                    text = entry.get('summary', '')
            except Exception as e:
                self.logger.warning(f"Failed to fetch full article content for {link}: {str(e)}")
                text = entry.get('summary', '')
            
            return {
                'title': title,
                'link': link,
                'text': text,
                'published': parse_date(entry.get('published', entry.get('updated', '')))
            }
        except Exception as e:
            self.logger.error(f"Failed to extract article: {str(e)}")
            return None