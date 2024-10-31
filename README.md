# RSS Feed Summarizer

An automated tool that fetches articles from RSS feeds, summarizes them using OpenAI's GPT models, and emails the summaries daily.

## Features

- Fetches articles from multiple RSS feeds
- Summarizes articles using OpenAI's GPT models
- Sends daily email digests with article summaries
- Caches processed articles to avoid duplicates
- Configurable time window for article processing
- Customizable summary prompts

## Prerequisites

- Python 3.8+
- Gmail account
- OpenAI API key
- Google App Password for Gmail

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ayyzad/rss-summarizer.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a Google App Password:
   - Go to your Google Account settings
   - Navigate to Security
   - Enable 2-Step Verification if not already enabled
   - Under "Signing in to Google," select "App passwords"
   - Generate a new app password for "Mail"
   - Copy the 16-character password

4. Create environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your OpenAI API key
   - Add your Gmail address
   - Add the Google App Password (not your regular Gmail password)
   - Add recipient email address

5. Configure RSS feeds:
   - Edit `config.json` to add your desired RSS feed URLs
   - Adjust settings in `config.py` if needed

## Usage

Run ad-hoc:
```bash
python main.py
```
Run scheduled (daily at 8:00 AM):
```bash
python main.py --schedule
```

## Project Structure

```plaintext
RSS-Summarizer/
├── articles/              # Stores JSON files of summarized articles
├── logs/                  # Log files directory
├── config.json           # RSS feed URLs configuration
├── config.py            # General configuration settings
├── email_sender.py     # Email functionality
├── feed_parser.py     # RSS feed parsing
├── main.py          # Main application entry point
├── summarizer.py   # OpenAI integration for summarization
└── article_cache.py   # Cache system for processed articles
```

## Configuration

### Feed Settings
Edit `config.json` to add or remove RSS feeds:
```json
{
    "feed_urls": [
"https://example.com/feed1.xml",
"https://example.com/feed2.xml"
    ]
}
```

### Application Settings
Adjust settings in `config.py`:
- `MAX_ARTICLES`: Maximum articles to process per feed
- `TIME_WINDOW`: Time window for article processing (in seconds)
- `SYSTEM_PROMPT`: Customize the summarization prompt
- Email settings (SMTP configuration)

## Logging

Logs are stored in `logs/feed_summarizer.log`. The log level can be adjusted in the code to show more or less detail.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

