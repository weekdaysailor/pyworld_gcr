"""Server configuration for World3 visualization."""
from app import app
import os

if __name__ == '__main__':
    try:
        # Create output directory if it doesn't exist
        os.makedirs('myworld3/output', exist_ok=True)
        print("Starting Flask server on port 8088...")
        # Initialize simulation data before starting server
        from app import run_simulations
        run_simulations()
        # Serve the Flask application
        app.run(host='0.0.0.0', port=8088, debug=True)
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        raise