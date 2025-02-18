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
        self.annual_increase_rate = 0.05  # 5% annual increase
        self.intensity_improvement_factor = 0.02  # Additional 2% annual improvement due to GCR

    def calculate_emission_intensity(self, year: int, industrial_output: float) -> float:
        """Calculate emission intensity with GCR policy effects."""
        try:
            # Get base intensity from parent class
            base_intensity = super().calculate_emission_intensity(year, industrial_output)

            if year < self.reward_start_year:
                return base_intensity

            # Calculate additional improvement from GCR policy
            years_with_gcr = year - self.reward_start_year
            gcr_improvement = (1 - self.intensity_improvement_factor) ** years_with_gcr

            return float(base_intensity * gcr_improvement)
        except Exception as e:
            print(f"Error calculating emission intensity: {str(e)}")
            return super().calculate_emission_intensity(year, industrial_output)

    def calculate_reward(self, year: int, co2e_emissions: float, industrial_output: float, 
                        emission_intensity: float) -> float:
        """Calculate carbon reward value based on CO2e emissions and intensity."""
        try:
            if year < self.reward_start_year:
                return 0.0

            # Calculate base reward with moderate year-over-year increase
            years_since_start = year - self.reward_start_year
            base_reward = self.initial_reward_value * (1 + years_since_start * self.annual_increase_rate)

            # Scale reward based on both absolute emissions and intensity
            emission_factor = 1.0 + (co2e_emissions / 1000)  # Per 1000 units of CO2e
            intensity_factor = 1.0 + (emission_intensity / self.base_intensity - 1)

            reward = float(base_reward * emission_factor * intensity_factor)

            # Cap maximum reward to prevent instability
            max_reward = self.initial_reward_value * 10
            reward = min(reward, max_reward)

            self.reward_history.append({
                'year': float(year),
                'reward_value': reward,
                'co2e_emissions': float(co2e_emissions),
                'emission_intensity': float(emission_intensity),
                'industrial_output': float(industrial_output)
            })

            return reward
        except Exception as e:
            print(f"Error calculating reward: {str(e)}")
            return 0.0

    def run_simulation(self) -> pd.DataFrame:
        """Run World3 simulation with GCR policy effects."""
        try:
            results = super().run_simulation()

            # Apply GCR effects with intensity-based modifiers
            for year in range(self.start_time, self.stop_time + 1):
                if year >= self.reward_start_year:
                    # Get current year's metrics
                    year_data = results.loc[year]
                    industrial_output = float(year_data['industrial_output'])
                    emission_intensity = float(year_data['emission_intensity'])
                    co2e_emissions = float(year_data['co2e_emissions'])

                    reward = self.calculate_reward(year, co2e_emissions, industrial_output, emission_intensity)

                    # Calculate impact modifiers based on reward
                    industrial_modifier = max(0.85, 1.0 - (reward * 0.001))  # Gentler impact on output
                    intensity_modifier = max(0.8, 1.0 - (reward * 0.002))   # Stronger impact on intensity

                    # Apply modifiers with shorter-term effects (5 years)
                    future_years = range(year, min(year + 5, self.stop_time + 1))
                    for future_year in future_years:
                        time_factor = 1.0 - (0.2 * (future_year - year))  # 20% reduction per year
                        if time_factor > 0:
                            # Update industrial output
                            results.loc[future_year, 'industrial_output'] *= industrial_modifier ** time_factor

                            # Recalculate intensity with GCR effects
                            results.loc[future_year, 'emission_intensity'] = self.calculate_emission_intensity(
                                future_year,
                                results.loc[future_year, 'industrial_output']
                            ) * intensity_modifier ** time_factor

                            # Update CO2e emissions
                            results.loc[future_year, 'co2e_emissions'] = (
                                results.loc[future_year, 'industrial_output'] *
                                results.loc[future_year, 'emission_intensity'] *
                                (1 + results.loc[future_year, 'persistent_pollution_index'] * 0.2)
                            )

            return results
        except Exception as e:
            print(f"Error in GCR simulation: {str(e)}")
            return super().run_simulation()

    def get_reward_history(self) -> pd.DataFrame:
        """Get history of carbon rewards and their effects."""
        return pd.DataFrame(self.reward_history)