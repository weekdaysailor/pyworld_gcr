"""Flask application for World3 visualization dashboard."""
from flask import Flask, render_template, jsonify, request
import os
import logging
import sys
from threading import Lock
from myworld3.models.base_model import BaseModel
from myworld3.models.gcr_model import GCRModel
from myworld3.utils.plotly_viz import create_simulation_dashboard

# Configure logging with more detail
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates')
app.secret_key = os.urandom(24)

# Store simulation results globally with thread safety
simulation_figures = {}
simulation_lock = Lock()

@app.route('/health')
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "healthy"}), 200

def run_simulations(xcc_price=100.0):
    """Run both baseline and GCR simulations."""
    try:
        logger.info("Starting simulations...")
        logger.info(f"Using XCC price: {xcc_price}")
        logger.info("Configuration: start_time=1900, stop_time=2100, dt=0.5")

        # Run baseline simulation
        baseline_model = BaseModel(
            start_time=1900,
            stop_time=2100,
            dt=0.5,
            target_population=0  # Keep original population values
        )
        logger.info("Running baseline simulation...")
        baseline_results = baseline_model.run_simulation()
        logger.info("Baseline simulation complete")

        # Log some basic statistics about the baseline results
        logger.info("Baseline simulation statistics:")
        logger.info(f"Number of timepoints: {len(baseline_results)}")
        logger.info(f"Population range: {baseline_results['population'].min():.2f} to {baseline_results['population'].max():.2f}")
        logger.info(f"Industrial output range: {baseline_results['industrial_output'].min():.2f} to {baseline_results['industrial_output'].max():.2f}")

        # Run GCR simulation with specified XCC price
        gcr_model = GCRModel(
            start_time=1900,
            stop_time=2100,
            dt=0.5,
            reward_start_year=2030,
            initial_reward_value=xcc_price,
            target_population=0  # Keep original population values
        )
        logger.info("Running GCR simulation...")
        logger.info(f"GCR policy starts in: 2030")
        gcr_results = gcr_model.run_simulation()
        logger.info("GCR simulation complete")

        # Log some basic statistics about the GCR results
        logger.info("GCR simulation statistics:")
        logger.info(f"Number of timepoints: {len(gcr_results)}")
        logger.info(f"Population range: {gcr_results['population'].min():.2f} to {gcr_results['population'].max():.2f}")
        logger.info(f"Industrial output range: {gcr_results['industrial_output'].min():.2f} to {gcr_results['industrial_output'].max():.2f}")

        # Generate Plotly figures with thread safety
        logger.info("Generating visualization...")
        try:
            with simulation_lock:
                global simulation_figures
                simulation_figures = create_simulation_dashboard(gcr_results, baseline_results)
            logger.info("Successfully created dashboard figures")
        except Exception as viz_error:
            logger.error(f"Error creating dashboard: {str(viz_error)}", exc_info=True)
            raise

        logger.info("Simulations completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error during simulations: {str(e)}", exc_info=True)
        return False

@app.route('/')
def dashboard():
    """Render the main dashboard."""
    try:
        logger.info("Received request to dashboard endpoint")
        with simulation_lock:
            if not simulation_figures:
                logger.info("No simulation results found, running simulations...")
                success = run_simulations()
                if not success:
                    error_msg = "Failed to run simulations. Check server logs for details."
                    logger.error(error_msg)
                    # Pass empty dictionary as fallback for plots
                    return render_template('dashboard.html', error=error_msg, plots={})

        logger.info("Rendering dashboard template")
        return render_template('dashboard.html', plots=simulation_figures)
    except Exception as e:
        error_msg = f"Error in dashboard route: {str(e)}"
        logger.error(error_msg, exc_info=True)
        # Always provide plots parameter, even if empty
        return render_template('dashboard.html', error=error_msg, plots={})

@app.route('/run')
def run_new_simulation():
    """Run a new simulation with specified XCC price and return updated plots."""
    try:
        xcc_price = float(request.args.get('xcc_price', 100))
        if xcc_price <= 0:
            return jsonify({'status': 'error', 'message': 'XCC price must be positive'}), 400

        logger.info(f"Received request to run new simulation with XCC price: {xcc_price}")
        if run_simulations(xcc_price):
            return jsonify({'status': 'success', 'message': 'Simulation completed successfully'})
        return jsonify({'status': 'error', 'message': 'Failed to run simulations'}), 500
    except ValueError as ve:
        error_msg = f"Invalid XCC price value: {str(ve)}"
        logger.error(error_msg)
        return jsonify({'status': 'error', 'message': error_msg}), 400
    except Exception as e:
        error_msg = f"Error in run_new_simulation route: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({'status': 'error', 'message': error_msg}), 500

if __name__ == '__main__':
    try:
        # Create output directory if it doesn't exist
        os.makedirs('myworld3/output', exist_ok=True)

        # Run initial simulation
        logger.info("Starting Flask application...")
        if not run_simulations():
            logger.warning("Initial simulation failed, but server will still start")

        # Get port from environment variable, default to 8080
        port = int(os.environ.get('PORT', 8080))
        logger.info(f'Starting Flask server on port {port}...')

        # Run the Flask application
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        logger.error(f'Failed to start Flask app: {str(e)}', exc_info=True)
        raise