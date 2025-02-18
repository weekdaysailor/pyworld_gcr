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

    # CO2e emissions comparison with components
    fig_co2e = go.Figure()

    # Plot baseline net emissions
    fig_co2e.add_trace(go.Scatter(
        x=convert_series(baseline_results.index),
        y=convert_series(baseline_results['net_emissions']),
        name='Baseline Net Emissions',
        line=dict(color='red')
    ))

    # Plot GCR scenario components
    fig_co2e.add_trace(go.Scatter(
        x=convert_series(gcr_results.index),
        y=convert_series(gcr_results['gross_emissions']),
        name='GCR Gross Emissions',
        line=dict(color='orange', dash='dot')
    ))

    fig_co2e.add_trace(go.Scatter(
        x=convert_series(gcr_results.index),
        y=convert_series(gcr_results['natural_uptake']),
        name='Natural Carbon Uptake',
        line=dict(color='green', dash='dash')
    ))

    fig_co2e.add_trace(go.Scatter(
        x=convert_series(gcr_results.index),
        y=convert_series(gcr_results['xcc_sequestration']),
        name='XCC Sequestration',
        line=dict(color='blue', dash='dash')
    ))

    fig_co2e.add_trace(go.Scatter(
        x=convert_series(gcr_results.index),
        y=convert_series(gcr_results['net_emissions']),
        name='GCR Net Emissions',
        line=dict(color='purple')
    ))

    # Update layout
    fig_co2e.update_layout(
        title='CO2e Emissions Components Over Time',
        xaxis_title='Year',
        yaxis_title='CO2e (Mt)',
        hovermode='x unified',
        template='plotly_white',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
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