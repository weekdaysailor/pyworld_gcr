"""Plotly visualization utilities for World3 simulation results."""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List
import json
import numpy as np

def create_simulation_dashboard(gcr_results: pd.DataFrame, baseline_results: pd.DataFrame) -> Dict[str, dict]:
    """Create interactive Plotly dashboard figures for simulation results."""
    figures = {}

    # Convert DataFrames to ensure JSON serializable values
    def convert_series(series):
        return [float(x) if isinstance(x, (np.floating, np.integer)) else x for x in series]

    # CO2e emissions comparison with historical data
    fig_co2e = go.Figure()

    # Plot baseline emissions
    fig_co2e.add_trace(go.Scatter(
        x=convert_series(baseline_results.index),
        y=convert_series(baseline_results['co2e_emissions']),
        name='Baseline Emissions',
        line=dict(color='red', dash='dash')
    ))

    # Plot GCR scenario emissions
    fig_co2e.add_trace(go.Scatter(
        x=convert_series(gcr_results.index),
        y=convert_series(gcr_results['co2e_emissions']),
        name='GCR Scenario Emissions',
        line=dict(color='blue')
    ))

    # Add emission intensity comparison
    fig_co2e.add_trace(go.Scatter(
        x=convert_series(gcr_results.index),
        y=convert_series(gcr_results['emission_intensity']),
        name='GCR Emission Intensity',
        line=dict(color='green', dash='dot'),
        yaxis='y2'
    ))

    # Update layout with dual y-axes
    fig_co2e.update_layout(
        title='CO2e Emissions and Intensity Over Time',
        xaxis_title='Year',
        yaxis_title='CO2e Emissions (Mt)',
        yaxis2=dict(
            title='Emission Intensity',
            overlaying='y',
            side='right'
        ),
        hovermode='x unified',
        template='plotly_white',
        showlegend=True
    )

    figures['co2e'] = fig_co2e.to_dict()

    # Population comparison
    fig_pop = go.Figure()
    fig_pop.add_trace(go.Scatter(
        x=convert_series(gcr_results.index - 2025),  # Years from 2025
        y=convert_series(gcr_results['population'] / 1000),  # Convert to billions
        name='GCR Scenario',
        line=dict(color='blue')
    ))
    fig_pop.add_trace(go.Scatter(
        x=convert_series(baseline_results.index - 2025),
        y=convert_series(baseline_results['population'] / 1000),
        name='Baseline',
        line=dict(color='red', dash='dash')
    ))
    fig_pop.update_layout(
        title='Global Population Projection',
        xaxis_title='Years from 2025',
        yaxis_title='Population (billions)',
        xaxis=dict(tickmode='linear', tick0=0, dtick=20),
        yaxis=dict(tickformat='.1f'),
        hovermode='x unified',
        template='plotly_white',
        showlegend=True
    )
    figures['population'] = fig_pop.to_dict()

    # Industrial output comparison
    fig_ind = go.Figure()
    fig_ind.add_trace(go.Scatter(
        x=convert_series(gcr_results.index - 2025),
        y=convert_series(gcr_results['industrial_output']),
        name='GCR Scenario',
        line=dict(color='blue')
    ))
    fig_ind.add_trace(go.Scatter(
        x=convert_series(baseline_results.index - 2025),
        y=convert_series(baseline_results['industrial_output']),
        name='Baseline',
        line=dict(color='red', dash='dash')
    ))
    fig_ind.update_layout(
        title='Industrial Output Projection',
        xaxis_title='Years from 2025',
        yaxis_title='Industrial Output Index',
        xaxis=dict(tickmode='linear', tick0=0, dtick=20),
        hovermode='x unified',
        template='plotly_white',
        showlegend=True
    )
    figures['industrial'] = fig_ind.to_dict()



    # Pollution comparison
    fig_pol = go.Figure()
    fig_pol.add_trace(go.Scatter(
        x=convert_series(gcr_results.index - 2025),
        y=convert_series(gcr_results['persistent_pollution_index']),
        name='GCR Scenario',
        line=dict(color='blue')
    ))
    fig_pol.add_trace(go.Scatter(
        x=convert_series(baseline_results.index - 2025),
        y=convert_series(baseline_results['persistent_pollution_index']),
        name='Baseline',
        line=dict(color='red', dash='dash')
    ))
    fig_pol.update_layout(
        title='Pollution Index Projection',
        xaxis_title='Years from 2025',
        yaxis_title='Pollution Index',
        xaxis=dict(tickmode='linear', tick0=0, dtick=20),
        hovermode='x unified',
        template='plotly_white',
        showlegend=True
    )
    figures['pollution'] = fig_pol.to_dict()

    return figures