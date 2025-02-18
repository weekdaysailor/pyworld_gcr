"""Flask application for World3 visualization dashboard."""
from flask import Flask, render_template, jsonify
import os
from myworld3.models.base_model import BaseModel
from myworld3.models.gcr_model import GCRModel
from myworld3.utils.plotly_viz import create_simulation_dashboard

app = Flask(__name__, template_folder='templates')
app.secret_key = os.urandom(24)

# Store simulation results globally
simulation_figures = {}

def run_simulations():
    """Run both baseline and GCR simulations."""
    try:
        print("Starting simulations...")
        # Run baseline simulation
        baseline_model = BaseModel(
            start_time=2025,
            stop_time=2125,
            dt=0.5,
            target_population=8000
        )
        print("Running baseline simulation...")
        baseline_results = baseline_model.run_simulation()
        print("Baseline simulation complete")

        # Run GCR simulation
        gcr_model = GCRModel(
            start_time=2025,
            stop_time=2125,
            dt=0.5,
            reward_start_year=2025,
            target_population=8000
        )
        print("Running GCR simulation...")
        gcr_results = gcr_model.run_simulation()
        print("GCR simulation complete")

        # Generate Plotly figures
        global simulation_figures
        print("Generating visualization...")
        simulation_figures = create_simulation_dashboard(gcr_results, baseline_results)
        print("Simulations completed successfully")
        return True
    except Exception as e:
        import traceback
        print(f"Error during simulations: {str(e)}")
        print("Traceback:")
        print(traceback.format_exc())
        return False

@app.route('/')
def dashboard():
    """Render the main dashboard."""
    try:
        if not simulation_figures:
            success = run_simulations()
            if not success:
                return render_template('simulation.html', error="Failed to run simulations")

        return render_template('dashboard.html', plots=simulation_figures)
    except Exception as e:
        return render_template('simulation.html', error=str(e))

@app.route('/run')
def run_new_simulation():
    """Run a new simulation and return updated plots."""
    try:
        if run_simulations():
            return jsonify({'status': 'success', 'message': 'Simulation completed successfully'})
        return jsonify({'status': 'error', 'message': 'Failed to run simulations'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # Create output directory if it doesn't exist
    os.makedirs('myworld3/output', exist_ok=True)
    # Run initial simulation
    if not run_simulations():
        print("WARNING: Initial simulation failed, but server will still start")
    app.run(host='0.0.0.0', port=8088, debug=True)