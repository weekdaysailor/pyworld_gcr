"""Server configuration for World3 visualization."""
# This file is deprecated. All server functionality has been moved to app.py
# Please use app.py directly for running the application.
from app import app
import os

if __name__ == '__main__':
    try:
        print("WARNING: This file is deprecated. Please use app.py instead.")
        print("Redirecting to app.py...")
        from app import run_simulations
        run_simulations()
        app.run(host='0.0.0.0', port=8088, debug=True)
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        raise