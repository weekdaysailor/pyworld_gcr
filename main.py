"""Main script for World3 simulation visualization."""
from myworld3.models.base_model import BaseModel
from myworld3.models.gcr_model import GCRModel
from myworld3.utils.plotting import create_time_series_plot, plot_gcr_analysis
import os

def run_simulations():
    """Run both baseline and GCR simulations."""
    # Run baseline simulation with 8 billion population and 2025 start
    baseline_model = BaseModel(
        start_time=2025,
        stop_time=2125,
        dt=0.5,
        target_population=8000  # 8 billion in millions
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

    return baseline_results, gcr_results

def main():
    """Generate visualization plots."""
    print("Running World3 simulations...")
    baseline_results, gcr_results = run_simulations()

    # Ensure output directory exists
    output_dir = 'myworld3/output'
    os.makedirs(output_dir, exist_ok=True)

    # List of metrics to plot
    metrics = [
        ('population', 'Population', 'Population (millions)'),
        ('industrial_output', 'Industrial Output', 'Output Index'),
        ('persistent_pollution_index', 'Pollution Index', 'Index Value'),
        ('co2e_emissions', 'CO2e Emissions', 'CO2e (Mt)'),
        ('food_per_capita', 'Food per Capita', 'Food Units'),
        ('service_output_per_capita', 'Service Output per Capita', 'Service Units'),
        ('resources', 'Non-Renewable Resources', 'Resource Units'),
        ('life_expectancy', 'Life Expectancy', 'Years')
    ]

    # Create static matplotlib plots for each metric
    for metric, title, ylabel in metrics:
        create_time_series_plot(
            baseline_results,
            [metric],
            f'{title} Over Time (Baseline)',
            ylabel,
            os.path.join(output_dir, f'baseline_results_{metric}_plot.png')
        )

    # Generate interactive HTML comparisons
    plot_gcr_analysis(gcr_results, baseline_results, output_dir)

    print("\nVisualization complete. Check the output directory for plots:")
    print(f"- Static PNG plots in: {output_dir}")
    print("- Interactive HTML comparisons (with _new suffix):")
    for metric, title, _ in metrics:
        print(f"  - {title}: {metric}_comparison_new.html")

if __name__ == '__main__':
    main()