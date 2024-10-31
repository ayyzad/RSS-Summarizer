from feed_parser import FeedParser
from summarizer import Summarizer
from email_sender import EmailSender
import json
from datetime import datetime
import schedule
import time
from logger import setup_logger
import argparse
import logging
from article_cache import ArticleCache

logger = setup_logger(__name__)

# Set logger to only show INFO and above (will skip DEBUG level messages)
logger.setLevel(logging.INFO)

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
                    'source': feed_url
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
    # Initialize cache
    cache = ArticleCache()
    
    # Load feed URLs from config
    with open('config.json', 'r') as f:
        config = json.load(f)
        feed_urls = config['feed_urls']
    
    logger.info("Starting daily run")
    all_summaries = []
    summarizer = Summarizer()
    
    for feed_url in feed_urls:
        logger.info(f"Processing feed: {feed_url}")
        parser = FeedParser(feed_url)
        
        try:
            articles = parser.parse_feed()
            logger.info(f"Found {len(articles)} articles in {feed_url}")
            
            for article in articles:
                try:
                    # Skip if already processed
                    if cache.is_processed(article['link']):
                        logger.info(f"Skipping already processed article: {article['title']}")
                        continue
                        
                    if 'text' in article and article['text']:
                        summary = summarizer.summarize(article['text'])
                        if summary:
                            all_summaries.append({
                                'title': article['title'],
                                'link': article['link'],
                                'summary': summary,
                                'published': article['published'].isoformat() if isinstance(article['published'], datetime) else article['published'],
                                'source': feed_url
                            })
                            # Add to cache after successful processing
                            cache.add_article(article['link'])
                            logger.info(f"Successfully summarized: {article['title']}")
                except Exception as e:
                    logger.error(f"Error processing article {article.get('title', 'Unknown')}: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing feed {feed_url}: {str(e)}")
    
    # Clean up old cache entries
    cache.cleanup_old_entries()
    
    # Only proceed if we have summaries
    if all_summaries:
        # Save summaries
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = f'/Users/azadneenan/Documents/RSS-Summarizer/articles/summaries_{timestamp}.json'
        
        try:
            with open(filepath, 'w') as f:
                json.dump(all_summaries, f, indent=2)
            logger.info(f"Saved {len(all_summaries)} summaries to {filepath}")
            
            # Send email
            logger.info("Sending email with summaries")
            email_sender = EmailSender()
            if email_sender.send_email(all_summaries):
                logger.info("Email sent successfully")
            else:
                logger.error("Failed to send email")
        except Exception as e:
            logger.error(f"Error saving summaries or sending email: {str(e)}")
    else:
        logger.warning("No summaries were generated")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='RSS Feed Summarizer')
    parser.add_argument('--schedule', action='store_true', 
                       help='Run in scheduled mode (daily at 08:00)')
    args = parser.parse_args()

    logger.info("Starting Feed Summarizer application")
    
    if args.schedule:
        logger.info("Running in scheduled mode")
        schedule.every().day.at("08:00").do(run_daily)
        logger.info("Scheduled daily run for 08:00")
        
        # Run immediately on start
        run_daily()
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        logger.info("Running in immediate mode (single run)")
        run_daily()
        logger.info("Single run completed")