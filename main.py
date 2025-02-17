"""Main script for World3 simulation visualization."""
from myworld3.models.base_model import BaseModel
from myworld3.models.gcr_model import GCRModel
from myworld3.utils.plotting import create_time_series_plot, plot_gcr_analysis

def run_simulations():
    """Run both baseline and GCR simulations."""
    # Run baseline simulation
    baseline_model = BaseModel()
    baseline_results = baseline_model.run_simulation()

    # Run GCR simulation
    gcr_model = GCRModel(reward_start_year=2025)
    gcr_results = gcr_model.run_simulation()

    return baseline_results, gcr_results

def main():
    """Generate visualization plots."""
    print("Running World3 simulations...")
    baseline_results, gcr_results = run_simulations()

    # Create static plots
    create_time_series_plot(
        baseline_results,
        ['population'],
        'Population Over Time (Baseline)',
        'Population',
        'myworld3/output/baseline_results_population_plot.png'
    )

    create_time_series_plot(
        baseline_results,
        ['industrial_output'],
        'Industrial Output Over Time (Baseline)',
        'Output',
        'myworld3/output/baseline_results_industrial_output_plot.png'
    )

    create_time_series_plot(
        baseline_results,
        ['persistent_pollution_index'],
        'Pollution Over Time (Baseline)',
        'Pollution Index',
        'myworld3/output/baseline_results_pollution_plot.png'
    )

    # Save comparative plots
    figures = plot_gcr_analysis(gcr_results, baseline_results)
    for name, fig in figures.items():
        fig.write_image(f'myworld3/output/gcr_{name}_comparison.png')

    print("Visualization complete. Check the output directory for plots.")

if __name__ == '__main__':
    main()