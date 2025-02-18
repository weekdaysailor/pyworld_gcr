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

    # CO2e emissions plot
    fig_co2e = go.Figure()

    # Get time series data
    years = convert_series(baseline_results.index)
    baseline_co2 = convert_series(baseline_results['atmospheric_co2'])
    gcr_co2 = convert_series(gcr_results['atmospheric_co2'])

    # Plot baseline Keeling curve
    fig_co2e.add_trace(go.Scatter(
        x=years,
        y=baseline_co2,
        name='Baseline CO₂ (Keeling Curve)',
        line=dict(color='red', shape='spline', smoothing=1.3)
    ))

    # Plot GCR scenario
    fig_co2e.add_trace(go.Scatter(
        x=years,
        y=gcr_co2,
        name='GCR CO₂ with XCC',
        line=dict(color='blue', shape='spline', smoothing=1.3)
    ))

    # Update layout with better axis configuration
    fig_co2e.update_layout(
        title='Atmospheric CO₂ Concentration Over Time',
        xaxis=dict(
            title='Year',
            tickmode='linear',
            tick0=1900,
            dtick=20,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            title='CO₂ (ppm)',
            gridcolor='lightgray',
            range=[min(baseline_co2) * 0.95, max(baseline_co2) * 1.05]
        ),
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

    # Mark transition points
    net_emissions = convert_series(gcr_results['net_emissions'])
    net_zero_year = None
    net_negative_year = None

    # Find transition years
    for i, (year, emission) in enumerate(zip(years, net_emissions)):
        if emission <= 0 and net_zero_year is None:
            net_zero_year = year
        elif net_zero_year and emission < 0 and net_negative_year is None:
            net_negative_year = year
            break

    # Add annotations if transition points exist
    if net_zero_year:
        fig_co2e.add_annotation(
            x=net_zero_year,
            y=gcr_co2[years.index(net_zero_year)],
            text='Net Zero',
            showarrow=True,
            arrowhead=1
        )

    if net_negative_year:
        fig_co2e.add_annotation(
            x=net_negative_year,
            y=gcr_co2[years.index(net_negative_year)],
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