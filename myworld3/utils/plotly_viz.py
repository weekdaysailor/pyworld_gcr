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

    # CO2e emissions converted to atmospheric concentration
    fig_co2e = go.Figure()

    # Generate atmospheric CO2 concentrations
    baseline_co2_ppm = convert_series(baseline_results['atmospheric_co2'])
    gcr_co2_ppm = convert_series(gcr_results['atmospheric_co2'])
    years = convert_series(baseline_results.index)

    # Plot baseline Keeling curve projection
    fig_co2e.add_trace(go.Scatter(
        x=years,
        y=baseline_co2_ppm,
        name='Baseline CO₂ (Keeling Curve)',
        line=dict(color='red')
    ))

    # Plot GCR scenario with XCC effects
    fig_co2e.add_trace(go.Scatter(
        x=years,
        y=gcr_co2_ppm,
        name='GCR CO₂ with XCC',
        line=dict(color='blue')
    ))

    # Update layout
    fig_co2e.update_layout(
        title='Atmospheric CO₂ Concentration Over Time',
        xaxis_title='Year',
        yaxis_title='CO₂ (ppm)',
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

    # Find transition points safely
    net_zero_year = None
    net_negative_year = None

    # Use numpy for safer array operations
    net_emissions = np.array(convert_series(gcr_results['net_emissions']))
    years_array = np.array(years)

    # Find first net-zero point
    zero_indices = np.where(net_emissions <= 0)[0]
    if len(zero_indices) > 0:
        net_zero_idx = zero_indices[0]
        net_zero_year = years_array[net_zero_idx]

        # Find first net-negative point after net-zero
        negative_indices = np.where((net_emissions < 0) & (years_array > net_zero_year))[0]
        if len(negative_indices) > 0:
            net_negative_idx = negative_indices[0]
            net_negative_year = years_array[net_negative_idx]

    # Add annotations if transition points are found
    if net_zero_year:
        fig_co2e.add_annotation(
            x=net_zero_year,
            y=gcr_co2_ppm[years.index(net_zero_year)],
            text='Net Zero',
            showarrow=True,
            arrowhead=1
        )

    if net_negative_year:
        fig_co2e.add_annotation(
            x=net_negative_year,
            y=gcr_co2_ppm[years.index(net_negative_year)],
            text='Net Negative',
            showarrow=True,
            arrowhead=1
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