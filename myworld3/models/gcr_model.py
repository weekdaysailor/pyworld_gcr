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
        self.max_sequestration_rate = 0.05  # Maximum 5% of emissions can be sequestered annually

    def calculate_xcc_sequestration(self, year: float, gross_emissions: float, reward: float) -> float:
        """Calculate carbon sequestration from XCC projects."""
        try:
            if year < self.reward_start_year:
                return 0.0

            # Calculate potential sequestration based on reward value and time
            years_active = year - self.reward_start_year
            reward_factor = reward / self.initial_reward_value

            # Sequestration capacity increases with time but has diminishing returns
            capacity_factor = 1.0 - np.exp(-0.1 * years_active)

            # Calculate sequestration potential
            max_potential = gross_emissions * self.max_sequestration_rate
            actual_sequestration = max_potential * capacity_factor * reward_factor * self.sequestration_efficiency

            return float(actual_sequestration)
        except Exception as e:
            print(f"Error calculating XCC sequestration: {str(e)}")
            return 0.0

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

    def calculate_co2e(self, year: int, industrial_output: float, pollution_index: float) -> Dict[str, float]:
        """Calculate CO2e emissions components and net emissions with GCR effects."""
        try:
            # Get base emissions calculation from parent class
            base_emissions = super().calculate_co2e(year, industrial_output, pollution_index)

            # For years before GCR policy starts, return base calculation
            if year < self.reward_start_year:
                return base_emissions

            # Calculate GCR-specific emission intensity
            gcr_intensity = self.calculate_emission_intensity(year, industrial_output)

            # Recalculate gross emissions with GCR intensity
            gross_emissions = industrial_output * gcr_intensity

            # Add pollution effects
            pollution_factor = 1.0 + (pollution_index * 0.2)
            total_emissions = gross_emissions * pollution_factor

            # Calculate natural uptake with GCR effects
            natural_uptake = total_emissions * self.natural_carbon_uptake

            # Calculate XCC sequestration (will be added during run_simulation)
            # Here we just calculate the components

            return {
                'gross_emissions': float(total_emissions),
                'natural_uptake': float(natural_uptake),
                'emission_intensity': float(gcr_intensity),
                'net_emissions': float(total_emissions - natural_uptake),  # XCC sequestration added later
            }
        except Exception as e:
            print(f"Error calculating GCR CO2e: {str(e)}")
            return {
                'gross_emissions': 0.0,
                'natural_uptake': 0.0,
                'emission_intensity': self.base_intensity,
                'net_emissions': 0.0
            }

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
            # Run base simulation to get initial results
            results = super().run_simulation()

            # Process each timestep for GCR effects
            for time in results.index:
                # Get current metrics
                industrial_output = float(results.loc[time, 'industrial_output'])
                pollution_index = float(results.loc[time, 'persistent_pollution_index'])

                # Get emissions data with GCR effects
                emissions_data = self.calculate_co2e(
                    int(time),
                    industrial_output,
                    pollution_index
                )

                # Calculate reward based on emissions
                reward = self.calculate_reward(
                    time,
                    emissions_data['gross_emissions'],
                    industrial_output,
                    emissions_data['emission_intensity']
                )

                # Calculate XCC sequestration
                xcc_seq = self.calculate_xcc_sequestration(
                    time,
                    emissions_data['gross_emissions'],
                    reward
                )

                # Store all components
                for key, value in emissions_data.items():
                    results.loc[time, key] = value

                results.loc[time, 'xcc_sequestration'] = xcc_seq

                # Update net emissions to include XCC sequestration
                results.loc[time, 'net_emissions'] = (
                    emissions_data['gross_emissions'] -
                    emissions_data['natural_uptake'] -
                    xcc_seq
                )

                # Apply GCR effects to other variables
                self.apply_gcr_effects(results, time, reward)

            return results

        except Exception as e:
            print(f"Error in GCR simulation: {str(e)}")
            raise

    def get_reward_history(self) -> pd.DataFrame:
        """Get history of carbon rewards and their effects."""
        return pd.DataFrame(self.reward_history)