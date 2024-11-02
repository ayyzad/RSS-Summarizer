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
    try:
        # Try to list config directory
        import os
        config_contents = os.listdir('/app/config') if os.path.exists('/app/config') else 'Directory not found'
        return jsonify({
            'status': 'healthy',
            'config_path': '/app/config',
            'config_contents': config_contents
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/run', methods=['POST'])
def trigger_run():
    try:
        logger.info("Received trigger request")
        
        # Debug: List all directories
        import os
        logger.info("Checking directories:")
        logger.info(f"Current directory: {os.getcwd()}")
        logger.info(f"Directory contents: {os.listdir('.')}")
        
        if os.path.exists('/app/config'):
            logger.info(f"Contents of /app/config: {os.listdir('/app/config')}")
        else:
            logger.error("/app/config directory not found")
        
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