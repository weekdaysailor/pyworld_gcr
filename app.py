"""Flask application for World3 visualization dashboard."""
from flask import Flask, render_template, jsonify
import os
from myworld3.models.base_model import BaseModel
from myworld3.models.gcr_model import GCRModel
from myworld3.utils.plotly_viz import create_simulation_dashboard

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Store simulation results globally
simulation_figures = {}

def run_simulations():
    """Run both baseline and GCR simulations."""
    # Run baseline simulation
    baseline_model = BaseModel(
        start_time=2025,
        stop_time=2125,
        dt=0.5,
        target_population=8000
    )
    baseline_results = baseline_model.run_simulation()

    # Run GCR simulation
    gcr_model = GCRModel(
        start_time=2025,
        stop_time=2125,
        dt=0.5,
        reward_start_year=2025,
        target_population=8000
    )
    gcr_results = gcr_model.run_simulation()

    # Generate Plotly figures
    global simulation_figures
    simulation_figures = create_simulation_dashboard(gcr_results, baseline_results)

@app.route('/')
def dashboard():
    """Render the main dashboard."""
    if not simulation_figures:
        run_simulations()

    plots = {
        'population': simulation_figures['population'].to_json(),
        'industrial': simulation_figures['industrial'].to_json(),
        'pollution': simulation_figures['pollution'].to_json()
    }
    return render_template('dashboard.html', plots=plots)

@app.route('/run')
def run_new_simulation():
    """Run a new simulation and return updated plots."""
    try:
        run_simulations()
        return jsonify({'status': 'success', 'message': 'Simulation completed successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # Create output directory if it doesn't exist
    os.makedirs('myworld3/output', exist_ok=True)
    # Run initial simulation
    run_simulations()
    app.run(host='0.0.0.0', port=8088, debug=True)