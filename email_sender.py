import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import (
    EMAIL_SENDER, 
    EMAIL_PASSWORD, 
    EMAIL_RECIPIENTS, 
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
        self.email_config = {
            'sender': EMAIL_SENDER,
            'password': EMAIL_PASSWORD,
            'recipients': [email.strip() for email in EMAIL_RECIPIENTS if email.strip()],  # Clean empty spaces
            'smtp_server': SMTP_SERVER,
            'smtp_port': SMTP_PORT
        }
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

        # Add summaries by category
        for category, category_summaries in categorized_summaries.items():
            category_display = category.replace('_', ' ').title()
            html += f"""
            <div class="category" id="{category}">
                <h2 class="category-title">{category_display} ({len(category_summaries)})</h2>
            """
            
            for summary in category_summaries:
                html += f"""
                <div class="article">
                    <h3><a href="{summary['link']}" class="title">{summary['title']}</a></h3>
                    <p class="meta">
                        <strong>Published:</strong> {summary['published']}<br>
                        <strong>Source:</strong> {summary['source']}
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
            msg['Subject'] = f"RSS Feed Summary - {datetime.now().strftime('%Y-%m-%d')}"
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