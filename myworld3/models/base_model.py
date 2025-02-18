"""Base model class for World3 simulations."""
from typing import Dict, Any, Optional, Union
import numpy as np
import pandas as pd
from pyworld3 import World3

class BaseModel:
    """Base class for World3-based models."""

    def __init__(self, start_time: int = 2025, stop_time: int = 2125, dt: float = 0.5,
                 target_population: Optional[float] = None):
        """Initialize the base model with normalized time scale."""
        # Validate time parameters
        if start_time < 2025:
            print(f"Warning: Adjusting start_time from {start_time} to minimum allowed year 2025")
            start_time = 2025

        if stop_time <= start_time:
            print(f"Warning: Adjusting stop_time to be 100 years after start_time")
            stop_time = start_time + 100

        if dt <= 0:
            print("Warning: Invalid dt value, setting to default 0.5")
            dt = 0.5

        self.start_time = start_time
        self.stop_time = stop_time
        self.dt = dt
        self.target_population = target_population
        self.world3: Optional[World3] = None
        self.results: Optional[pd.DataFrame] = None
        self.base_intensity = 2.5  # Base CO2e intensity per unit of industrial output
        self.tech_improvement_rate = 0.01  # 1% annual improvement in base technology

    def calculate_emission_intensity(self, year: int, industrial_output: float) -> float:
        """Calculate emission intensity factor considering technological improvements."""
        years_passed = year - self.start_time
        # Technological improvement reduces base intensity over time
        tech_factor = (1 - self.tech_improvement_rate) ** years_passed
        # Scale factor based on industrial output (economies of scale)
        scale_factor = 1.0 + (np.log(industrial_output / 100) * 0.1)
        return float(self.base_intensity * tech_factor * scale_factor)

    def calculate_co2e(self, year: int, industrial_output: float, pollution_index: float) -> float:
        """Calculate CO2 equivalent emissions based on industrial output and pollution."""
        # Get base intensity adjusted for technology and scale
        intensity = self.calculate_emission_intensity(year, industrial_output)

        # Calculate base emissions
        base_co2e = industrial_output * intensity

        # Additional emissions from pollution feedback
        pollution_multiplier = 1.0 + (pollution_index * 0.2)  # 20% increase per unit of pollution

        return float(base_co2e * pollution_multiplier)

    def scale_population(self) -> None:
        """Scale population and related factors to match target population while maintaining balance."""
        if self.target_population is None or self.world3 is None:
            return

        # Calculate current total from cohorts
        current_total = (self.world3.p1i + self.world3.p2i + 
                        self.world3.p3i + self.world3.p4i)

        # Calculate scaling factor
        scaling_factor = float(self.target_population) / float(current_total)

        print(f"\nScaling system by factor: {scaling_factor:.4f}")
        print("Initial state:")
        print(f"Population:        {current_total:.2f} million")
        print(f"Industrial Output: {self.world3.ici:.2f}")
        print(f"Food Production:   {self.world3.ali:.2f}")
        print(f"Service Output:    {self.world3.sci:.2f}")

        # Scale population cohorts
        self.world3.p1i *= scaling_factor   # 0-14 years
        self.world3.p2i *= scaling_factor   # 15-44 years
        self.world3.p3i *= scaling_factor   # 45-64 years
        self.world3.p4i *= scaling_factor   # 65+ years

        # Scale industrial and agricultural systems
        self.world3.ici *= scaling_factor * 0.9   # Industrial capital
        self.world3.ali *= scaling_factor * 0.95  # Arable land
        self.world3.sfpc *= 1.0                   # Food per capita remains constant (using correct attribute)

        # Scale service sector and capital
        self.world3.sci *= scaling_factor * 0.85  # Service capital

        # Resource and pollution adjustments
        self.world3.nri *= scaling_factor * 0.8   # Non-renewable resources
        self.world3.ppolx *= scaling_factor * 0.7 # Persistent pollution

        # Recalculate total population after scaling
        new_total = (self.world3.p1i + self.world3.p2i + 
                    self.world3.p3i + self.world3.p4i)

        print("\nScaled state:")
        print(f"Population:        {new_total:.2f} million")
        print(f"Industrial Output: {self.world3.ici:.2f}")
        print(f"Food Production:   {self.world3.ali:.2f}")
        print(f"Service Output:    {self.world3.sci:.2f}")

    def initialize_model(self) -> None:
        """Initialize the World3 model with basic parameters."""
        print("Initializing World3 model...")
        try:
            # Create World3 instance with time parameters
            self.world3 = World3(
                year_min=self.start_time,
                year_max=self.stop_time,
                dt=self.dt,
                pyear=1975,  # Policy year
                verbose=True  # Enable verbose mode for debugging
            )

            if self.world3 is None:
                raise RuntimeError("Failed to initialize World3 model")

            # Initialize World3 state
            print("Setting up World3 constants and variables...")
            self.world3.init_world3_constants()

            # Initialize each subsystem - constants first
            print("Initializing subsystem constants...")
            self.world3.init_population_constants()
            self.world3.init_capital_constants()
            self.world3.init_agriculture_constants()
            self.world3.init_pollution_constants()
            self.world3.init_resource_constants()

            # Initialize variables after scaling
            print("\nInitializing subsystem variables...")
            self.world3.init_population_variables()
            self.world3.init_capital_variables()
            self.world3.init_agriculture_variables()
            self.world3.init_pollution_variables()
            self.world3.init_resource_variables()

            # Set up table and delay functions
            print("Setting up subsystem functions...")
            self.world3.set_population_table_functions()
            self.world3.set_population_delay_functions()
            self.world3.set_capital_table_functions()
            self.world3.set_capital_delay_functions()
            self.world3.set_agriculture_table_functions()
            self.world3.set_agriculture_delay_functions()
            self.world3.set_pollution_table_functions()
            self.world3.set_pollution_delay_functions()
            self.world3.set_resource_table_functions()
            self.world3.set_resource_delay_functions()

            # Initialize exogenous inputs and global functions
            self.world3.init_exogenous_inputs()
            print("Setting up World3 global functions...")
            self.world3.set_world3_table_functions()
            self.world3.set_world3_delay_functions()

            # Scale population if target is set
            if self.target_population is not None:
                self.scale_population()

        except Exception as e:
            print(f"Error during World3 initialization: {str(e)}")
            raise

    def run_simulation(self) -> pd.DataFrame:
        """Run the World3 simulation and return results."""
        if self.world3 is None:
            print("Initializing model before simulation...")
            self.initialize_model()

        if self.world3 is None:
            raise RuntimeError("Failed to initialize World3 model")

        try:
            print("Running World3 simulation...")
            self.world3.run_world3()

            print("Processing simulation results...")
            time_series = np.arange(self.start_time, self.stop_time + self.dt, self.dt)

            # Base variables - using correct attribute names from PyWorld3
            vars_dict = {
                'population': self.world3.pop,
                'industrial_output': self.world3.io,
                'persistent_pollution_index': self.world3.ppol,
                'population_0_14': self.world3.p1,
                'population_15_44': self.world3.p2,
                'population_45_64': self.world3.p3,
                'population_65_plus': self.world3.p4,
                'food_per_capita': self.world3.sfpc,  # Using correct attribute name
                'service_output_per_capita': self.world3.sopc,
                'resources': self.world3.nrfr,
                'life_expectancy': self.world3.le
            }

            # Create initial DataFrame
            self.results = pd.DataFrame(vars_dict, index=time_series)

            # Calculate emission intensity and CO2e for each timestep
            self.results['emission_intensity'] = self.results.apply(
                lambda row: self.calculate_emission_intensity(
                    int(row.name),  # year
                    row['industrial_output']
                ),
                axis=1
            )

            self.results['co2e_emissions'] = self.results.apply(
                lambda row: self.calculate_co2e(
                    int(row.name),  # year
                    row['industrial_output'],
                    row['persistent_pollution_index']
                ),
                axis=1
            )

            print("Simulation completed successfully.")
            return self.results

        except Exception as e:
            print(f"Error during simulation: {str(e)}")
            raise

    def get_variables(self) -> Dict[str, Any]:
        """Get all available variables in the model."""
        if self.world3 is None:
            return {}

        try:
            return {
                var: getattr(self.world3, var)
                for var in dir(self.world3)
                if not var.startswith('_') and not callable(getattr(self.world3, var))
            }
        except Exception as e:
            print(f"Error getting variables: {str(e)}")
            return {}