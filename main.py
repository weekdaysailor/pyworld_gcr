"""Main application for World3 simulation visualization."""
from flask import Flask, render_template, jsonify
import pandas as pd
from myworld3.models.base_model import BaseModel
from myworld3.models.gcr_model import GCRModel
from myworld3.utils.plotting import plot_gcr_analysis
import plotly
import json

app = Flask(__name__)

def run_simulations():
    """Run both baseline and GCR simulations."""
    # Run baseline simulation
    baseline_model = BaseModel()
    baseline_results = baseline_model.run_simulation()
    
    # Run GCR simulation
    gcr_model = GCRModel(reward_start_year=2025)
    gcr_results = gcr_model.run_simulation()
    
    return baseline_results, gcr_results

@app.route('/')
def index():
    """Render main visualization page."""
    baseline_results, gcr_results = run_simulations()
    figures = plot_gcr_analysis(gcr_results, baseline_results)
    
    # Convert Plotly figures to JSON for rendering
    plots_json = {
        name: json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        for name, fig in figures.items()
    }
    
    return render_template('index.html', plots=plots_json)

@app.route('/api/simulation/results')
def get_simulation_results():
    """API endpoint for raw simulation results."""
    baseline_results, gcr_results = run_simulations()
    
    return jsonify({
        'baseline': baseline_results.to_dict(orient='records'),
        'gcr': gcr_results.to_dict(orient='records')
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
