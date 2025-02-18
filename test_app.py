from flask import Flask
import logging
import sys
import os

# Configure logging with more detail
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def hello():
    logger.info('Received request to root endpoint')
    return 'Hello! Flask test environment is working!'

if __name__ == '__main__':
    try:
        # Get port from environment variable with fallback to 3000
        port = int(os.environ.get('PORT', 3000))
        logger.info(f'Starting Flask application on port {port}...')
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        logger.error(f'Failed to start Flask app: {str(e)}')
        raise