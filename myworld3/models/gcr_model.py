"""Global Carbon Reward model implementation."""
from typing import Dict, Any, Optional, List, Union
import numpy as np
import pandas as pd
from .base_model import BaseModel

class GCRModel(BaseModel):
    """World3 model with Global Carbon Reward policy implementation."""

    def __init__(self, 
                 start_time: int = 1900,
                 stop_time: int = 2100,
                 dt: float = 0.5,
                 reward_start_year: int = 2025,
                 initial_reward_value: float = 100.0,
                 target_population: Optional[float] = None):
        """Initialize the GCR model.

        Args:
            start_time: Start year for simulation
            stop_time: End year for simulation
            dt: Time step for simulation
            reward_start_year: Year to start implementing GCR policy
            initial_reward_value: Initial value of carbon reward ($/tCO2e)
            target_population: Target total population in millions for 2025 (if None, uses default)
        """
        super().__init__(start_time, stop_time, dt, target_population)
        self.reward_start_year = reward_start_year
        self.initial_reward_value = initial_reward_value
        self.reward_history: List[Dict[str, float]] = []

    def initialize_model(self) -> None:
        """Initialize the World3 model with GCR parameters."""
        super().initialize_model()
        if self.world3 is not None:
            # Update policy year in World3 instance
            self.world3.pyear = self.reward_start_year

    def calculate_reward(self, year: int, emissions: float, industrial_output: float) -> float:
        """Calculate carbon reward value for given year and emissions."""
        if year < self.reward_start_year:
            return 0.0

        # Enhanced reward calculation with progressive scaling
        years_since_start = year - self.reward_start_year
        base_reward = self.initial_reward_value * (1 + years_since_start * 0.02)  # 2% annual increase

        # Scale based on both emissions and industrial output with safe float conversion
        emission_factor = 1.0 + (abs(float(emissions)) / 500)  # More aggressive scaling
        industrial_factor = 1.0 + (abs(float(industrial_output)) / 1000)

        reward = float(base_reward * emission_factor * industrial_factor)

        self.reward_history.append({
            'year': float(year),
            'reward_value': reward,
            'emissions': float(emissions)
        })

        return reward

    def run_simulation(self) -> pd.DataFrame:
        """Run World3 simulation with GCR policy effects."""
        results = super().run_simulation()

        # Apply GCR effects with enhanced impact
        for year in range(self.start_time, self.stop_time + 1):
            if year >= self.reward_start_year:
                # Calculate emissions based on industrial output and pollution with safe float conversion
                industrial_output = abs(float(results.loc[year, 'industrial_output']))
                pollution_level = abs(float(results.loc[year, 'persistent_pollution_index']))
                emissions = industrial_output * (0.5 + pollution_level * 0.1)  # Enhanced emissions calculation

                reward = self.calculate_reward(year, emissions, industrial_output)

                # Enhanced impact calculations with stronger effects
                industrial_modifier = max(0.1, 1.0 - (reward * 0.01))  # 1% reduction per reward unit, minimum 90% reduction
                pollution_modifier = max(0.1, 1.0 - (reward * 0.015))  # 1.5% reduction per reward unit, minimum 90% reduction

                # Apply modifiers with temporal delay
                future_years = range(year, min(year + 5, self.stop_time + 1))
                for future_year in future_years:
                    # Gradual impact that increases over time
                    time_factor = max(0, 1.0 - (0.2 * (future_year - year)))  # 20% reduction per year

                    if time_factor > 0:
                        current_industrial = float(results.loc[future_year, 'industrial_output'])
                        current_pollution = float(results.loc[future_year, 'persistent_pollution_index'])

                        results.loc[future_year, 'industrial_output'] = current_industrial * (industrial_modifier ** time_factor)
                        results.loc[future_year, 'persistent_pollution_index'] = current_pollution * (pollution_modifier ** time_factor)

        return results

    def get_reward_history(self) -> pd.DataFrame:
        """Get history of carbon rewards and their effects.

        Returns:
            DataFrame containing reward history
        """
        return pd.DataFrame(self.reward_history)