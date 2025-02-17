"""Main script for World3 simulation visualization."""
from myworld3.models.base_model import BaseModel
from myworld3.models.gcr_model import GCRModel
from myworld3.utils.plotting import create_time_series_plot, plot_gcr_analysis
import os

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

    # Ensure output directory exists
    output_dir = 'myworld3/output'
    os.makedirs(output_dir, exist_ok=True)

    # Create static matplotlib plots
    create_time_series_plot(
        baseline_results,
        ['population'],
        'Population Over Time (Baseline)',
        'Population',
        os.path.join(output_dir, 'baseline_results_population_plot.png')
    )

    create_time_series_plot(
        baseline_results,
        ['industrial_output'],
        'Industrial Output Over Time (Baseline)',
        'Output',
        os.path.join(output_dir, 'baseline_results_industrial_output_plot.png')
    )

    create_time_series_plot(
        baseline_results,
        ['persistent_pollution_index'],
        'Pollution Over Time (Baseline)',
        'Pollution Index',
        os.path.join(output_dir, 'baseline_results_pollution_plot.png')
    )

    # Generate interactive HTML comparisons
    plot_gcr_analysis(gcr_results, baseline_results, output_dir)

    print("Visualization complete. Check the output directory for plots:")
    print(f"- Static PNG plots in: {output_dir}")
    print("- Interactive HTML comparisons (with _new suffix):")
    print("  - Population: population_comparison_new.html")
    print("  - Industrial Output: industrial_output_comparison_new.html")
    print("  - Pollution: pollution_comparison_new.html")

if __name__ == '__main__':
    main()