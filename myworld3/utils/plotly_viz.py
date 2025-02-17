"""Plotly visualization utilities for World3 simulation results."""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List

def create_simulation_dashboard(gcr_results: pd.DataFrame, baseline_results: pd.DataFrame) -> Dict[str, go.Figure]:
    """Create interactive Plotly dashboard figures for simulation results.

    Args:
        gcr_results: Results from GCR model
        baseline_results: Results from baseline model

    Returns:
        Dictionary containing Plotly figures
    """
    figures = {}
    
    # Population comparison
    fig_pop = go.Figure()
    fig_pop.add_trace(go.Scatter(
        x=gcr_results.index,
        y=gcr_results['population'],
        name='GCR Scenario',
        line=dict(color='blue')
    ))
    fig_pop.add_trace(go.Scatter(
        x=baseline_results.index,
        y=baseline_results['population'],
        name='Baseline',
        line=dict(color='red')
    ))
    fig_pop.update_layout(
        title='Population Comparison',
        xaxis_title='Year',
        yaxis_title='Population (millions)',
        hovermode='x unified',
        template='plotly_white'
    )
    figures['population'] = fig_pop

    # Industrial output comparison
    fig_ind = go.Figure()
    fig_ind.add_trace(go.Scatter(
        x=gcr_results.index,
        y=gcr_results['industrial_output'],
        name='GCR Scenario',
        line=dict(color='blue')
    ))
    fig_ind.add_trace(go.Scatter(
        x=baseline_results.index,
        y=baseline_results['industrial_output'],
        name='Baseline',
        line=dict(color='red')
    ))
    fig_ind.update_layout(
        title='Industrial Output Comparison',
        xaxis_title='Year',
        yaxis_title='Industrial Output',
        hovermode='x unified',
        template='plotly_white'
    )
    figures['industrial'] = fig_ind

    # Pollution comparison
    fig_pol = go.Figure()
    fig_pol.add_trace(go.Scatter(
        x=gcr_results.index,
        y=gcr_results['persistent_pollution_index'],
        name='GCR Scenario',
        line=dict(color='blue')
    ))
    fig_pol.add_trace(go.Scatter(
        x=baseline_results.index,
        y=baseline_results['persistent_pollution_index'],
        name='Baseline',
        line=dict(color='red')
    ))
    fig_pol.update_layout(
        title='Pollution Index Comparison',
        xaxis_title='Year',
        yaxis_title='Pollution Index',
        hovermode='x unified',
        template='plotly_white'
    )
    figures['pollution'] = fig_pol

    return figures
