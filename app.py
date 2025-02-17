"""Flask application for World3 visualization dashboard."""
from flask import Flask, render_template, send_from_directory
import os
from myworld3.models.base_model import BaseModel
from myworld3.models.gcr_model import GCRModel

app = Flask(__name__, 
           static_folder='myworld3/output',
           static_url_path='/static/output')
app.secret_key = os.urandom(24)

@app.route('/')
@app.route('/dashboard')
@app.route('/view_plots.html')  # Add compatibility route
def dashboard():
    """Render the main dashboard."""
    return render_template('dashboard.html')

@app.route('/run')
def run_simulation():
    """Run a new simulation and display results."""
    try:
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

        return render_template(
            'simulation.html',
            message="Simulation completed successfully"
        )
    except Exception as e:
        return render_template(
            'simulation.html',
            error=str(e)
        )

if __name__ == '__main__':
    # Create output directory if it doesn't exist
    os.makedirs('myworld3/output', exist_ok=True)
    app.run(host='0.0.0.0', port=8081, debug=True)