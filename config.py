import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Feed Configuration
MAX_ARTICLES = 5
TIME_WINDOW = 86400  # 24 hours in seconds

# Summarization Configuration
SYSTEM_PROMPT = """You are a professional content analyzer and summarizer. 
You analyze articles and categorize them while creating concise summaries.
Always return your response in a valid JSON format with 'summary' and 'category' fields."""

SUMMARY_PROMPT = """Please analyze the following article and:
1. Create a brief 2-3 sentence summary focusing on the main points
2. Categorize it into one of these categories: crypto/blockchain, venture_capital, us_news, world_news, tech_news, business, finance, science, energy, sports, other

Return your response in this JSON format:
{
    "summary": "your 2-3 sentence summary here",
    "category": "one_of_the_predefined_categories"
}"""

# Email Configuration
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
# Can be comma-separated string in .env file
EMAIL_RECIPIENTS = os.getenv('EMAIL_RECIPIENTS', '').split(',')
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465