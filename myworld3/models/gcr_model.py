"""Global Carbon Reward model implementation."""
from typing import Dict, Any, Optional, List, Union
import numpy as np
import pandas as pd
from .base_model import BaseModel

class GCRModel(BaseModel):
    """World3 model with Global Carbon Reward policy implementation."""

    def __init__(self, 
                 start_time: int = 2025,
                 stop_time: int = 2125,
                 dt: float = 0.5,
                 reward_start_year: int = 2025,
                 initial_reward_value: float = 100.0,
                 target_population: Optional[float] = None):
        """Initialize the GCR model with normalized time scale."""
        super().__init__(start_time, stop_time, dt, target_population)

        # Validate and normalize reward start year
        if reward_start_year < start_time:
            print(f"Warning: Adjusting reward_start_year from {reward_start_year} to match start_time {start_time}")
            reward_start_year = start_time

        self.reward_start_year = reward_start_year
        self.initial_reward_value = initial_reward_value
        self.reward_history: List[Dict[str, float]] = []
        self.annual_increase_rate = 0.05  # 5% annual increase
        self.intensity_improvement_factor = 0.02  # Additional 2% annual improvement due to GCR
        self.base_intensity = 1.0  # Base carbon intensity factor
        self.co2e_per_industrial_unit = 0.5  # CO2e emissions per unit of industrial output

    def calculate_emission_intensity(self, year: int, industrial_output: float) -> float:
        """Calculate emission intensity with GCR policy effects."""
        try:
            # Calculate base intensity with technological improvement
            base_intensity = self.base_intensity * (0.98 ** (year - self.start_time))  # 2% natural improvement

            if year < self.reward_start_year:
                return base_intensity

            # Calculate additional improvement from GCR policy
            years_with_gcr = year - self.reward_start_year
            gcr_improvement = (1 - self.intensity_improvement_factor) ** years_with_gcr

            return float(base_intensity * gcr_improvement)
        except Exception as e:
            print(f"Error calculating emission intensity: {str(e)}")
            return self.base_intensity

    def calculate_co2e_emissions(self, industrial_output: float, emission_intensity: float,
                               pollution_index: float) -> float:
        """Calculate CO2e emissions based on industrial output and current intensity."""
        try:
            # Base emissions from industrial output
            base_emissions = industrial_output * emission_intensity * self.co2e_per_industrial_unit

            # Additional emissions from pollution feedback
            pollution_factor = 1.0 + (pollution_index * 0.2)  # 20% increase per unit of pollution index

            return float(base_emissions * pollution_factor)
        except Exception as e:
            print(f"Error calculating CO2e emissions: {str(e)}")
            return 0.0

    def calculate_reward(self, year: int, co2e_emissions: float, industrial_output: float, 
                        emission_intensity: float) -> float:
        """Calculate carbon reward value based on CO2e emissions and intensity."""
        try:
            if year < self.reward_start_year:
                return 0.0

            # Calculate base reward with moderate year-over-year increase
            years_since_start = year - self.reward_start_year
            base_reward = self.initial_reward_value * (1 + self.annual_increase_rate * years_since_start)

            # Scale reward based on emissions relative to industrial output
            emission_intensity_ratio = emission_intensity / self.base_intensity
            reward_scalar = 1.0 + np.log1p(emission_intensity_ratio)  # Logarithmic scaling for better stability

            reward = float(base_reward * reward_scalar)

            # Cap maximum reward to prevent instability
            max_reward = self.initial_reward_value * 5
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

    def apply_gcr_effects(self, results: pd.DataFrame, year: int, reward: float) -> None:
        """Apply GCR policy effects to various model parameters."""
        try:
            # Calculate impact modifiers based on reward with gentler effects
            industrial_modifier = max(0.92, 1.0 - (reward * 0.0005))  # Gentler impact on industry
            pollution_modifier = max(0.90, 1.0 - (reward * 0.0008))   # Gentler impact on pollution
            food_modifier = max(0.95, 1.0 - (reward * 0.0003))       # Very gentle impact on food
            service_modifier = max(0.93, 1.0 - (reward * 0.0004))    # Gentle impact on services

            # Apply modifiers with shorter time horizon and smoother decay
            future_years = range(year, min(year + 3, self.stop_time + 1))
            for future_year in future_years:
                # Use exponential decay instead of linear
                time_delta = future_year - year
                time_factor = np.exp(-0.5 * time_delta)  # Smoother decay

                if time_factor > 0.1:  # Only apply significant effects
                    # Update industrial output with smoothing
                    current_industrial = results.loc[future_year, 'industrial_output']
                    new_industrial = current_industrial * (industrial_modifier ** time_factor)
                    results.loc[future_year, 'industrial_output'] = (
                        current_industrial * 0.7 + new_industrial * 0.3  # Blend old and new values
                    )

                    # Update pollution index with smoother transition
                    current_pollution = results.loc[future_year, 'persistent_pollution_index']
                    new_pollution = current_pollution * (pollution_modifier ** time_factor)
                    results.loc[future_year, 'persistent_pollution_index'] = (
                        current_pollution * 0.8 + new_pollution * 0.2  # More weight on current value
                    )

                    # Update food per capita with minimal disruption
                    current_food = results.loc[future_year, 'food_per_capita']
                    new_food = current_food * (food_modifier ** time_factor)
                    results.loc[future_year, 'food_per_capita'] = (
                        current_food * 0.9 + new_food * 0.1  # Mostly preserve current value
                    )

                    # Update service output with smooth transition
                    current_service = results.loc[future_year, 'service_output_per_capita']
                    new_service = current_service * (service_modifier ** time_factor)
                    results.loc[future_year, 'service_output_per_capita'] = (
                        current_service * 0.8 + new_service * 0.2  # Blend for smooth transition
                    )

                    # Life expectancy changes should be very gradual
                    base_life_expectancy = results.loc[future_year, 'life_expectancy']
                    pollution_effect = 1.0 - (0.02 * (1.0 - pollution_modifier) * time_factor)
                    service_effect = 1.0 + (0.01 * (1.0 - service_modifier) * time_factor)
                    new_life_expectancy = base_life_expectancy * pollution_effect * service_effect
                    results.loc[future_year, 'life_expectancy'] = (
                        base_life_expectancy * 0.95 + new_life_expectancy * 0.05  # Very gradual change
                    )

        except Exception as e:
            print(f"Error applying GCR effects: {str(e)}")

    def run_simulation(self) -> pd.DataFrame:
        """Run World3 simulation with GCR policy effects."""
        try:
            results = super().run_simulation()

            # Initialize CO2e emissions column if not present
            if 'co2e_emissions' not in results.columns:
                results['co2e_emissions'] = 0.0

            # Apply GCR effects with intensity-based modifiers
            for year in range(self.start_time, self.stop_time + 1):
                # Get current year's metrics
                year_data = results.loc[year]
                industrial_output = float(year_data['industrial_output'])

                # Calculate emission intensity for current year
                emission_intensity = self.calculate_emission_intensity(year, industrial_output)
                results.loc[year, 'emission_intensity'] = emission_intensity

                # Calculate CO2e emissions
                pollution_index = float(year_data['persistent_pollution_index'])
                co2e_emissions = self.calculate_co2e_emissions(industrial_output, emission_intensity, pollution_index)
                results.loc[year, 'co2e_emissions'] = co2e_emissions

                if year >= self.reward_start_year:
                    # Calculate and apply GCR effects
                    reward = self.calculate_reward(year, co2e_emissions, industrial_output, emission_intensity)
                    self.apply_gcr_effects(results, year, reward)

            return results
        except Exception as e:
            print(f"Error in GCR simulation: {str(e)}")
            return super().run_simulation()

    def get_reward_history(self) -> pd.DataFrame:
        """Get history of carbon rewards and their effects."""
        return pd.DataFrame(self.reward_history)