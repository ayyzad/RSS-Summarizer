import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Feed Configuration
MAX_ARTICLES = 20
TIME_WINDOW = 86400  # 24 hours in seconds

# Summarization Configuration
SYSTEM_PROMPT = """You are a professional content summarizer. 
Create concise, informative summaries that capture the key points."""

SUMMARY_PROMPT = """Please provide a brief summary of the following article 
in 2-3 sentences, focusing on the main points:"""

# Email Configuration
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')  # App-specific password for Gmail
EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT')
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587