"""Server configuration for World3 visualization."""
from app import app
import os

if __name__ == '__main__':
    # Create output directory if it doesn't exist
    os.makedirs('myworld3/output', exist_ok=True)
    # Serve the Flask application
    app.run(host='0.0.0.0', port=8081, debug=True)