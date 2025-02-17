from flask import Flask
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def hello():
    logger.info('Received request to root endpoint')
    return 'Hello! Flask test environment is working!'

if __name__ == '__main__':
    try:
        logger.info('Starting Flask application...')
        app.run(host='0.0.0.0', port=3000, debug=True)
    except Exception as e:
        logger.error(f'Failed to start Flask app: {str(e)}')
        raise