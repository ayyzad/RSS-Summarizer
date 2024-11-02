from flask import Flask
import threading
from main import main
import os

app = Flask(__name__)

# Start the RSS summarizer in a background thread
def run_summarizer():
    main()

@app.route('/')
def health_check():
    return 'RSS Summarizer is running', 200

if __name__ == '__main__':
    # Start the summarizer in a background thread
    summarizer_thread = threading.Thread(target=run_summarizer)
    summarizer_thread.daemon = True
    summarizer_thread.start()
    
    # Start the web server
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port) 