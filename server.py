from flask import Flask, jsonify
import threading
from main import run_daily
import os
import traceback
from logger import setup_logger

app = Flask(__name__)
logger = setup_logger(__name__)

@app.route('/', methods=['GET'])
def health_check():
    return 'RSS Summarizer is running', 200

@app.route('/run', methods=['POST'])
def trigger_run():
    try:
        logger.info("Received trigger request")
        # List contents of /app/config
        logger.info(f"Contents of /app/config: {os.listdir('/app/config')}")
        
        run_daily()
        logger.info("Run completed successfully")
        return jsonify({'status': 'success', 'message': 'RSS summarizer run completed'}), 200
    except Exception as e:
        error_msg = f"Error during run: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port) 