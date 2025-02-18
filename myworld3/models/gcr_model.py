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
        """Initialize the GCR model."""
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

        # More aggressive reward scaling with stronger year-over-year increase
        years_since_start = year - self.reward_start_year
        base_reward = self.initial_reward_value * (1 + years_since_start * 0.15)  # Increased to 15% annual increase

        # Enhanced scaling factors with stronger response to emissions and industrial output
        emission_factor = 1.0 + (abs(float(emissions)) / 50)  # More aggressive scaling
        industrial_factor = 1.0 + (abs(float(industrial_output)) / 100)

        reward = float(base_reward * emission_factor * industrial_factor)

        # Cap the maximum reward to prevent instability
        max_reward = self.initial_reward_value * 20  # Increased cap
        reward = min(reward, max_reward)

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
                # Calculate emissions based on industrial output and pollution
                industrial_output = abs(float(results.loc[year, 'industrial_output']))
                pollution_level = abs(float(results.loc[year, 'persistent_pollution_index']))

                # Enhanced emissions calculation with stronger pollution feedback
                emissions = industrial_output * (1.0 + pollution_level * 0.5)  # Increased pollution feedback

                reward = self.calculate_reward(year, emissions, industrial_output)

                # Stronger impact calculations
                industrial_modifier = max(0.5, 1.0 - (reward * 0.008))  # Increased reduction per reward unit
                pollution_modifier = max(0.4, 1.0 - (reward * 0.01))   # Increased reduction per reward unit

                # Apply modifiers with cumulative effects
                future_years = range(year, min(year + 10, self.stop_time + 1))
                for future_year in future_years:
                    time_factor = 1.0 - (0.1 * (future_year - year))  # 10% reduction per year
                    if time_factor > 0:
                        results.loc[future_year, 'industrial_output'] *= industrial_modifier ** time_factor
                        results.loc[future_year, 'persistent_pollution_index'] *= pollution_modifier ** time_factor

        return results

    def get_reward_history(self) -> pd.DataFrame:
        """Get history of carbon rewards and their effects."""
        return pd.DataFrame(self.reward_history)