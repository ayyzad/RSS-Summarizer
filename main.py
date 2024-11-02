from feed_parser import FeedParser
from summarizer import Summarizer
from email_sender import EmailSender
import json
from datetime import datetime
import schedule
import time
from logger import setup_logger, log_section, log_summary
import argparse
import logging
from article_cache import ArticleCache
import os
from pathlib import Path

logger = setup_logger(__name__)

# Set logger to only show INFO and above (will skip DEBUG level messages)
logger.setLevel(logging.INFO)

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)
    feed_urls = config['feed_urls']  # Get feed URLs from config

def process_feeds(feed_urls):
    logger.info("Starting feed processing")
    summarizer = Summarizer()
    summaries = []

    for feed_url in feed_urls:
        logger.info(f"Processing feed: {feed_url}")
        parser = FeedParser(feed_url)
        articles = parser.parse_feed()
        
        for article in articles:
            logger.debug(f"Summarizing article: {article['title']}")
            summary = summarizer.summarize(article['text'])
            if summary:
                summaries.append({
                    'title': article['title'],
                    'link': article['link'],
                    'summary': summary,
                    'published': article['published'].isoformat(),
                    'source': feed_url,
                    'category': article['category']
                })

    # Save summaries
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = '/Users/azadneenan/Documents/RSS-Summarizer/articles'
    filename = f'summaries_{timestamp}.json'
    filepath = f'{output_dir}/{filename}'
    logger.info(f"Saving {len(summaries)} summaries to {filepath}")
    
    try:
        with open(filepath, 'w') as f:
            json.dump(summaries, f, indent=2)
        logger.info("Summaries saved successfully")
    except Exception as e:
        logger.error(f"Error saving summaries: {str(e)}")

    # Send email
    logger.info("Initiating email sending")
    email_sender = EmailSender()
    if email_sender.send_email(summaries):
        logger.info("Email sent successfully")
    else:
        logger.error("Failed to send email")

def run_daily():
    logger = setup_logger(__name__)
    summarizer = Summarizer()
    cache = ArticleCache()
    all_summaries = []
    
    logger.info("Starting daily run")
    
    total_feeds = len(feed_urls)
    processed_feeds = 0
    
    for feed_url in feed_urls:
        processed_feeds += 1
        logger.info(f"Progress: {processed_feeds}/{total_feeds} feeds ({(processed_feeds/total_feeds)*100:.1f}%)")
        logger.info(f"Processing feed: {feed_url}")
        
        try:
            parser = FeedParser(feed_url)  # Create parser once
            articles = parser.parse_feed()  # Parse feed once
            
            if not articles:
                logger.warning(f"No articles found in {feed_url}")
                continue
                
            logger.info(f"Found {len(articles)} articles in {feed_url}")
            
            # Process only new articles
            new_articles = []
            for article in articles:
                is_cached = cache.is_processed(article['link'])
                logger.info(f"Article {article['link']} cached: {is_cached}")
                if not is_cached:
                    new_articles.append(article)
            if new_articles:
                logger.info(f"Found {len(new_articles)} new articles to process")
                for article in new_articles:
                    summary = summarizer.summarize(article['text'])
                    if summary:
                        cache.add_article(article['link'])
                        summary_with_metadata = {
                            'title': article['title'],
                            'link': article['link'],
                            'published': article['published'],
                            'source': feed_url,
                            **summary  # Unpack the summary and category
                        }
                        all_summaries.append(summary_with_metadata)
            else:
                logger.info("Found 0 new articles to process")
                
        except Exception as e:
            logger.error(f"Error processing feed {feed_url}: {str(e)}")

    if all_summaries:
        # Convert datetime objects to strings before saving
        formatted_summaries = []
        for summary in all_summaries:
            formatted_summary = summary.copy()
            if 'published' in formatted_summary:
                formatted_summary['published'] = formatted_summary['published'].isoformat()
            formatted_summaries.append(formatted_summary)
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Get project root directory and create output path
        project_root = Path(__file__).parent
        output_dir = project_root / 'articles' / 'summaries'
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f'summaries_{timestamp}.json'
        filepath = output_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(formatted_summaries, f, indent=2)
            logger.info(f"Summaries saved successfully to {filepath}")
        except Exception as e:
            logger.error(f"Error saving summaries: {str(e)}")

        # Send email
        logger.info("Initiating email sending")
        email_sender = EmailSender()
        if email_sender.send_summaries(all_summaries):
            logger.info("Email sent successfully")
        else:
            logger.error("Failed to send email")
    else:
        logger.warning("No summaries to save or send")

def main():
    logger = setup_logger(__name__)
    logger.info("Starting Feed Summarizer application")
    
    # Schedule jobs
    schedule.every().day.at("09:00").do(run_daily)
    schedule.every().day.at("17:00").do(run_daily)
    
    logger.info("Scheduled jobs: 9:00 AM and 5:00 PM daily")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='RSS Feed Summarizer')
    parser.add_argument('--run-once', action='store_true', help='Run once and exit')
    args = parser.parse_args()
    
    if args.run_once:
        logger.info("Running single execution")
        run_daily()
    else:
        logger.info("Starting scheduled execution")
        main()