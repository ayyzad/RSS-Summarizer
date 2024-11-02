import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import (
    EMAIL_SENDER, 
    EMAIL_PASSWORD, 
    SMTP_SERVER, 
    SMTP_PORT
)
from logger import setup_logger
import json
from datetime import datetime

logger = setup_logger(__name__)

class EmailSender:
    def __init__(self):
        self.logger = setup_logger(__name__)
        
        # Load config file for recipients
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        self.email_config = {
            'sender': EMAIL_SENDER,
            'password': EMAIL_PASSWORD,
            'recipients': config.get('email_recipients', []),  # Get recipients from config.json
            'smtp_server': SMTP_SERVER,
            'smtp_port': SMTP_PORT
        }
        # Add category order
        self.category_order = [
            'us_news',
            'world_news',
            'tech_news',
            'business',
            'crypto/blockchain',
            'science',
            'health',
            'other'
        ]
        self.logger.info("Initialized EmailSender")

    def format_summaries_to_html(self, summaries):
        logger.debug("Formatting summaries to HTML")
        
        # Group summaries by category
        categorized_summaries = {}
        for summary in summaries:
            category = summary.get('category', 'uncategorized')
            if category not in categorized_summaries:
                categorized_summaries[category] = []
            categorized_summaries[category].append(summary)

        # Get unknown categories and add them to the order list
        unknown_categories = set(categorized_summaries.keys()) - set(self.category_order)
        if unknown_categories:
            self.logger.warning(f"Found unknown categories: {', '.join(unknown_categories)}")
            categories_to_display = self.category_order + list(unknown_categories)
        else:
            categories_to_display = self.category_order

        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
                .category { margin-bottom: 40px; }
                .category-title { 
                    color: #1a73e8; 
                    text-transform: uppercase; 
                    padding-bottom: 10px;
                    border-bottom: 2px solid #1a73e8;
                    margin-bottom: 20px;
                }
                .article { 
                    margin-bottom: 30px; 
                    border-bottom: 1px solid #eee; 
                    padding-bottom: 20px; 
                }
                .title { 
                    color: #2c3e50; 
                    text-decoration: none;
                    font-size: 1.2em;
                }
                .title:hover { text-decoration: underline; }
                .meta { 
                    color: #7f8c8d; 
                    font-size: 0.9em;
                    margin: 8px 0;
                }
                .summary { 
                    color: #34495e;
                    margin-top: 10px;
                }
            </style>
        </head>
        <body>
        """

        # Add summaries by category in specified order
        for category in categories_to_display:
            if category in categorized_summaries:
                category_summaries = categorized_summaries[category]
                category_display = category.replace('_', ' ').title()
                html += f"""
                <div class="category" id="{category}">
                    <h2 class="category-title">{category_display} ({len(category_summaries)})</h2>
                """
                
                for summary in category_summaries:
                    # Format the date to show only Month Day, Year
                    try:
                        if isinstance(summary['published'], str):
                            published_date = datetime.fromisoformat(summary['published'])
                        else:
                            published_date = summary['published']
                        formatted_date = published_date.strftime('%B %d, %Y')  # e.g., "March 1, 2024"
                    except Exception as e:
                        self.logger.warning(f"Error formatting date: {e}")
                        formatted_date = "Date unavailable"  # fallback if date parsing fails
                    
                    html += f"""
                    <div class="article">
                        <h3><a href="{summary['link']}" class="title">{summary['title']}</a></h3>
                        <p class="meta">
                            <strong>Published:</strong> {formatted_date}
                        </p>
                        <p class="summary">{summary['summary']}</p>
                    </div>
                    """
                
                html += "</div>"
        
        html += "</body></html>"
        logger.debug("HTML formatting completed")
        return html

    def send_summaries(self, summaries):
        try:
            if not summaries:
                self.logger.warning("No summaries to send")
                return False

            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Daily News Brief - {datetime.now().strftime('%Y-%m-%d')}"
            msg['From'] = self.email_config['sender']
            # Set primary recipient as the sender (or first recipient)
            msg['To'] = self.email_config['sender']
            # Add BCC recipients (hidden from other recipients)
            msg['Bcc'] = ', '.join(self.email_config['recipients'])
            
            # Create HTML content
            html_content = self.format_summaries_to_html(summaries)
            msg.attach(MIMEText(html_content, 'html'))

            # Send email
            with smtplib.SMTP_SSL(self.email_config['smtp_server'], 
                                self.email_config['smtp_port']) as server:
                server.login(self.email_config['sender'], 
                           self.email_config['password'])
                # Send to all recipients (including BCCs)
                server.sendmail(
                    self.email_config['sender'],
                    [self.email_config['sender']] + self.email_config['recipients'],  # Include sender in recipient list
                    msg.as_string()
                )

            self.logger.info(f"Successfully sent email to {len(self.email_config['recipients'])} BCC recipients with {len(summaries)} summaries")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send email: {str(e)}")
            return False