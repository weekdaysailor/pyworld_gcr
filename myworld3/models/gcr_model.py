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
                 reward_start_year: int = 2030,
                 initial_reward_value: float = 100.0,
                 target_population: Optional[float] = None):
        """Initialize the GCR model."""
        super().__init__(start_time, stop_time, dt, target_population)
        self.reward_start_year = reward_start_year
        self.initial_reward_value = initial_reward_value
        self.reward_history: List[Dict[str, float]] = []
        self.annual_increase_rate = 0.05  # 5% annual increase
        self.intensity_improvement_factor = 0.02  # Additional 2% annual improvement due to GCR
        self.sequestration_efficiency = 0.85  # 85% efficiency in carbon sequestration projects
        self.min_sequestration_years = 100  # Minimum years for carbon sequestration
        self.natural_carbon_uptake = 0.1 # 10% natural carbon uptake


    def calculate_emission_intensity(self, year: float, industrial_output: float) -> float:
        """Calculate emission intensity with GCR policy effects."""
        try:
            # Calculate base intensity with technological improvement
            base_intensity = super().calculate_emission_intensity(int(year), industrial_output)

            if year < self.reward_start_year:
                return base_intensity

            # Calculate XCC-driven improvements
            years_with_gcr = year - self.reward_start_year

            # XCC effectiveness increases with reward value and time
            # But has diminishing returns
            xcc_effect = (1.0 - np.exp(-0.05 * years_with_gcr)) * (
                self.sequestration_efficiency * 
                min(1.0, self.intensity_improvement_factor * years_with_gcr)
            )

            return float(base_intensity * (1.0 - xcc_effect))
        except Exception as e:
            print(f"Error calculating emission intensity: {str(e)}")
            return self.base_intensity

    def calculate_co2e_emissions(self, industrial_output: float, emission_intensity: float,
                               pollution_index: float) -> float:
        """Calculate CO2e emissions based on industrial output and current intensity."""
        try:
            # Base emissions from industrial output
            base_emissions = industrial_output * emission_intensity

            # Additional emissions from pollution feedback
            pollution_factor = 1.0 + (pollution_index * 0.2)

            # Account for natural carbon sinks and XCC sequestration
            net_emissions = base_emissions * pollution_factor

            # Apply natural uptake (simplified carbon cycle)
            natural_uptake = net_emissions * self.natural_carbon_uptake

            return float(net_emissions - natural_uptake)
        except Exception as e:
            print(f"Error calculating CO2e emissions: {str(e)}")
            return 0.0

    def calculate_reward(self, year: float, co2e_emissions: float, industrial_output: float, 
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

    def apply_gcr_effects(self, results: pd.DataFrame, year: float, reward: float) -> None:
        """Apply GCR policy effects to various model parameters."""
        try:
            if year < self.reward_start_year:
                return  # No effects before policy starts

            # Calculate impact modifiers with continuous scaling
            years_active = year - self.reward_start_year
            policy_strength = 1.0 - np.exp(-0.1 * years_active)  # Smooth ramp-up of policy effects

            base_reward_effect = reward / self.initial_reward_value
            effect_strength = np.tanh(0.5 * base_reward_effect)  # Bounded effect strength

            # Calculate modifiers with smooth transitions
            industrial_modifier = 1.0 - (0.08 * effect_strength * policy_strength)
            pollution_modifier = 1.0 - (0.12 * effect_strength * policy_strength)
            food_modifier = 1.0 - (0.05 * effect_strength * policy_strength)
            service_modifier = 1.0 - (0.07 * effect_strength * policy_strength)

            # Apply modifiers directly to current year
            current_industrial = results.loc[year, 'industrial_output']
            results.loc[year, 'industrial_output'] = current_industrial * industrial_modifier

            current_pollution = results.loc[year, 'persistent_pollution_index']
            results.loc[year, 'persistent_pollution_index'] = current_pollution * pollution_modifier

            current_food = results.loc[year, 'food_per_capita']
            results.loc[year, 'food_per_capita'] = current_food * food_modifier

            current_service = results.loc[year, 'service_output_per_capita']
            results.loc[year, 'service_output_per_capita'] = current_service * service_modifier

            # Update life expectancy with smooth transitions
            current_life = results.loc[year, 'life_expectancy']
            life_modifier = 1.0 + (0.02 * effect_strength * policy_strength)  # Small positive effect
            results.loc[year, 'life_expectancy'] = current_life * life_modifier

        except Exception as e:
            print(f"Error applying GCR effects: {str(e)}")

    def run_simulation(self) -> pd.DataFrame:
        """Run World3 simulation with GCR policy effects."""
        try:
            # Run base simulation first
            results = super().run_simulation()

            # Initialize CO2e emissions column if not present
            if 'co2e_emissions' not in results.columns:
                results['co2e_emissions'] = 0.0
            if 'emission_intensity' not in results.columns:
                results['emission_intensity'] = 1.0

            # Create time points array with proper dt steps
            time_points = np.arange(self.start_time, self.stop_time + self.dt, self.dt)

            # Apply GCR effects for each time point
            for time in time_points:
                # Get current time's metrics
                industrial_output = float(results.loc[time, 'industrial_output'])

                # Calculate emission intensity for current time
                emission_intensity = self.calculate_emission_intensity(time, industrial_output)
                results.loc[time, 'emission_intensity'] = emission_intensity

                # Calculate CO2e emissions
                pollution_index = float(results.loc[time, 'persistent_pollution_index'])
                co2e_emissions = self.calculate_co2e_emissions(industrial_output, emission_intensity, pollution_index)
                results.loc[time, 'co2e_emissions'] = co2e_emissions

                # Calculate and apply GCR effects
                reward = self.calculate_reward(time, co2e_emissions, industrial_output, emission_intensity)
                self.apply_gcr_effects(results, time, reward)

            return results

        except Exception as e:
            print(f"Error in GCR simulation: {str(e)}")
            return super().run_simulation()

    def get_reward_history(self) -> pd.DataFrame:
        """Get history of carbon rewards and their effects."""
        return pd.DataFrame(self.reward_history)