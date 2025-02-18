"""Flask application for World3 visualization dashboard."""
from flask import Flask, render_template, jsonify
import os
import logging
import sys
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

# Store simulation results globally
simulation_figures = {}

def run_simulations():
    """Run both baseline and GCR simulations."""
    try:
        logger.info("Starting simulations...")
        # Run baseline simulation
        baseline_model = BaseModel(
            start_time=2025,
            stop_time=2125,
            dt=0.5,
            target_population=8000
        )
        logger.info("Running baseline simulation...")
        baseline_results = baseline_model.run_simulation()
        logger.info("Baseline simulation complete")

        # Run GCR simulation
        gcr_model = GCRModel(
            start_time=2025,
            stop_time=2125,
            dt=0.5,
            reward_start_year=2025,
            target_population=8000
        )
        logger.info("Running GCR simulation...")
        gcr_results = gcr_model.run_simulation()
        logger.info("GCR simulation complete")

        # Generate Plotly figures
        global simulation_figures
        logger.info("Generating visualization...")
        simulation_figures = create_simulation_dashboard(gcr_results, baseline_results)
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
        if not simulation_figures:
            logger.info("No simulation results found, running simulations...")
            success = run_simulations()
            if not success:
                logger.error("Failed to run simulations")
                return render_template('simulation.html', error="Failed to run simulations")

        logger.info("Rendering dashboard template")
        return render_template('dashboard.html', plots=simulation_figures)
    except Exception as e:
        logger.error(f"Error in dashboard route: {str(e)}", exc_info=True)
        return render_template('simulation.html', error=str(e))

@app.route('/run')
def run_new_simulation():
    """Run a new simulation and return updated plots."""
    try:
        logger.info("Received request to run new simulation")
        if run_simulations():
            return jsonify({'status': 'success', 'message': 'Simulation completed successfully'})
        return jsonify({'status': 'error', 'message': 'Failed to run simulations'}), 500
    except Exception as e:
        logger.error(f"Error in run_new_simulation route: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    try:
        # Create output directory if it doesn't exist
        os.makedirs('myworld3/output', exist_ok=True)

        logger.info("Starting Flask application...")
        # Run initial simulation
        if not run_simulations():
            logger.warning("Initial simulation failed, but server will still start")

        logger.info(f'Starting Flask server on port 8088...')
        app.run(host='0.0.0.0', port=8088, debug=True)
    except Exception as e:
        logger.error(f'Failed to start Flask app: {str(e)}', exc_info=True)
        raise