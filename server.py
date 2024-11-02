from flask import Flask
from main import run_daily
import os

app = Flask(__name__)

@app.route('/')
def health_check():
    return 'RSS Summarizer is running', 200

@app.route('/run', methods=['POST'])
def trigger_run():
    try:
        run_daily()
        return 'RSS summarizer run completed', 200
    except Exception as e:
        return f'Error: {str(e)}', 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port) 