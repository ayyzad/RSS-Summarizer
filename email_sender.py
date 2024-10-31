import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import (
    EMAIL_SENDER, 
    EMAIL_PASSWORD, 
    EMAIL_RECIPIENT, 
    SMTP_SERVER, 
    SMTP_PORT
)
from logger import setup_logger

logger = setup_logger(__name__)

class EmailSender:
    def __init__(self):
        self.sender = EMAIL_SENDER
        self.password = EMAIL_PASSWORD
        self.recipient = EMAIL_RECIPIENT
        logger.info("Initialized EmailSender")

    def format_summaries_to_html(self, summaries):
        logger.debug("Formatting summaries to HTML")
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; }
                .article { margin-bottom: 30px; border-bottom: 1px solid #eee; padding-bottom: 20px; }
                .title { color: #2c3e50; text-decoration: none; }
                .title:hover { text-decoration: underline; }
                .meta { color: #7f8c8d; font-size: 0.9em; }
                .summary { color: #34495e; }
            </style>
        </head>
        <body>
        """
        
        for summary in summaries:
            html += f"""
            <div class="article">
                <h2><a href="{summary['link']}" class="title">{summary['title']}</a></h2>
                <p class="meta">
                    <strong>Published:</strong> {summary['published']}<br>
                    <strong>Source:</strong> {summary['source']}
                </p>
                <p class="summary">{summary['summary']}</p>
            </div>
            """
        
        html += "</body></html>"
        logger.debug("HTML formatting completed")
        return html

    def send_email(self, summaries):
        logger.info(f"Preparing to send email with {len(summaries)} summaries")
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Daily Feed Summaries - {len(summaries)} Articles"
        msg['From'] = self.sender
        msg['To'] = self.recipient

        html_content = self.format_summaries_to_html(summaries)
        msg.attach(MIMEText(html_content, 'html'))

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                logger.debug("SMTP TLS connection established")
                server.login(self.sender, self.password)
                logger.debug("SMTP login successful")
                server.send_message(msg)
                logger.info("Email sent successfully")
                return True
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False