"""Plotting utilities for World3 simulation results."""
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from typing import Dict, List, Optional
import pandas as pd

def create_time_series_plot(
    data: pd.DataFrame,
    variables: List[str],
    title: str,
    ylabel: str,
    save_path: Optional[str] = None
) -> None:
    """Create and save a time series plot.
    
    Args:
        data: DataFrame containing simulation results
        variables: List of variables to plot
        title: Plot title
        ylabel: Y-axis label
        save_path: Path to save the plot (optional)
    """
    plt.figure(figsize=(12, 6))
    
    for var in variables:
        plt.plot(data.index, data[var], label=var)
    
    plt.title(title)
    plt.xlabel('Year')
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()

def create_interactive_plot(
    data: pd.DataFrame,
    variables: List[str],
    title: str
) -> go.Figure:
    """Create an interactive Plotly figure.
    
    Args:
        data: DataFrame containing simulation results
        variables: List of variables to plot
        title: Plot title
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    for var in variables:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data[var],
                name=var,
                mode='lines'
            )
        )
    
    fig.update_layout(
        title=title,
        xaxis_title='Year',
        yaxis_title='Value',
        hovermode='x unified'
    )
    
    return fig

def plot_gcr_analysis(gcr_results: pd.DataFrame, baseline_results: pd.DataFrame) -> Dict[str, go.Figure]:
    """Create comparative plots between GCR and baseline scenarios.
    
    Args:
        gcr_results: Results from GCR model
        baseline_results: Results from baseline model
        
    Returns:
        Dictionary of Plotly figures
    """
    figures = {}
    
    # Population comparison
    figures['population'] = create_interactive_plot(
        pd.concat([
            gcr_results['population'].rename('GCR Scenario'),
            baseline_results['population'].rename('Baseline')
        ], axis=1),
        ['GCR Scenario', 'Baseline'],
        'Population Comparison'
    )
    
    # Industrial output comparison
    figures['industrial_output'] = create_interactive_plot(
        pd.concat([
            gcr_results['industrial_output'].rename('GCR Scenario'),
            baseline_results['industrial_output'].rename('Baseline')
        ], axis=1),
        ['GCR Scenario', 'Baseline'],
        'Industrial Output Comparison'
    )
    
    # Pollution comparison
    figures['pollution'] = create_interactive_plot(
        pd.concat([
            gcr_results['persistent_pollution_index'].rename('GCR Scenario'),
            baseline_results['persistent_pollution_index'].rename('Baseline')
        ], axis=1),
        ['GCR Scenario', 'Baseline'],
        'Pollution Index Comparison'
    )
    
    return figures
