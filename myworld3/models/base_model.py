"""Base model class for World3 simulations."""
from typing import Dict, Any, Optional, Union
import numpy as np
import pandas as pd
from pyworld3 import World3

class BaseModel:
    """Base class for World3-based models."""

    def __init__(self, start_time: int = 1900, stop_time: int = 2100, dt: float = 0.5,
                 target_population: Optional[float] = None):
        """Initialize the base model.

        Args:
            start_time: Start year for simulation
            stop_time: End year for simulation
            dt: Time step for simulation
            target_population: Target total population in millions for 2025 (if None, uses default)
        """
        self.start_time = start_time
        self.stop_time = stop_time
        self.dt = dt
        self.target_population = target_population
        self.world3: Optional[World3] = None
        self.results: Optional[pd.DataFrame] = None

    def scale_population(self) -> None:
        """Scale population cohorts to match target population while maintaining distribution."""
        if self.target_population is None or self.world3 is None:
            return

        # Calculate current total from cohorts
        current_total = (self.world3.p1i + self.world3.p2i + 
                        self.world3.p3i + self.world3.p4i)

        # Calculate scaling factor with proper formatting
        scaling_factor = float(self.target_population) / float(current_total)

        print(f"\nScaling population by factor: {scaling_factor:.4f}")
        print("Initial population distribution:")
        print(f"Ages 0-14:  {self.world3.p1i:.2f} million")
        print(f"Ages 15-44: {self.world3.p2i:.2f} million")
        print(f"Ages 45-64: {self.world3.p3i:.2f} million")
        print(f"Ages 65+:   {self.world3.p4i:.2f} million")
        print(f"Total:      {current_total:.2f} million")

        # Scale each cohort
        self.world3.p1i = float(self.world3.p1i * scaling_factor)  # 0-14 years
        self.world3.p2i = float(self.world3.p2i * scaling_factor)  # 15-44 years
        self.world3.p3i = float(self.world3.p3i * scaling_factor)  # 45-64 years
        self.world3.p4i = float(self.world3.p4i * scaling_factor)  # 65+ years

        new_total = (self.world3.p1i + self.world3.p2i + 
                    self.world3.p3i + self.world3.p4i)

        print("\nScaled population distribution:")
        print(f"Ages 0-14:  {self.world3.p1i:.2f} million")
        print(f"Ages 15-44: {self.world3.p2i:.2f} million")
        print(f"Ages 45-64: {self.world3.p3i:.2f} million")
        print(f"Ages 65+:   {self.world3.p4i:.2f} million")
        print(f"Total:      {new_total:.2f} million")

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

            # Scale population if target is set (before variables initialization)
            if self.target_population is not None:
                self.scale_population()

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

            vars_dict = {
                'population': self.world3.pop,
                'industrial_output': self.world3.io,
                'persistent_pollution_index': self.world3.ppol,
                'population_0_14': self.world3.p1,
                'population_15_44': self.world3.p2,
                'population_45_64': self.world3.p3,
                'population_65_plus': self.world3.p4
            }

            self.results = pd.DataFrame(vars_dict, index=time_series)
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