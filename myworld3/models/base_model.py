"""Base model class for World3 simulations."""
from typing import Dict, Any
import numpy as np
import pandas as pd
from pyworld3 import World3

class BaseModel:
    """Base class for World3-based models."""

    def __init__(self, start_time: int = 1900, stop_time: int = 2100, dt: float = 0.5):
        """Initialize the base model.

        Args:
            start_time: Start year for simulation
            stop_time: End year for simulation
            dt: Time step for simulation
        """
        self.start_time = start_time
        self.stop_time = stop_time
        self.dt = dt
        self.world3 = None
        self.results = None

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

            # Initialize World3 state
            print("Setting up World3 constants and variables...")
            self.world3.init_world3_constants()
            self.world3.init_world3_variables()

            # Initialize each subsystem
            print("Initializing subsystems...")
            # Population subsystem
            self.world3.init_population_constants()
            self.world3.init_population_variables()
            self.world3.set_population_table_functions()
            self.world3.set_population_delay_functions()

            # Capital subsystem
            self.world3.init_capital_constants()
            self.world3.init_capital_variables()
            self.world3.set_capital_table_functions()
            self.world3.set_capital_delay_functions()

            # Agriculture subsystem
            self.world3.init_agriculture_constants()
            self.world3.init_agriculture_variables()
            self.world3.set_agriculture_table_functions()
            self.world3.set_agriculture_delay_functions()

            # Pollution subsystem
            self.world3.init_pollution_constants()
            self.world3.init_pollution_variables()
            self.world3.set_pollution_table_functions()
            self.world3.set_pollution_delay_functions()

            # Resource subsystem
            self.world3.init_resource_constants()
            self.world3.init_resource_variables()
            self.world3.set_resource_table_functions()
            self.world3.set_resource_delay_functions()

            # Initialize exogenous inputs
            self.world3.init_exogenous_inputs()

            # Set global World3 functions
            print("Setting up World3 global functions...")
            self.world3.set_world3_table_functions()
            self.world3.set_world3_delay_functions()

        except Exception as e:
            print(f"Error during World3 initialization: {str(e)}")
            raise

    def run_simulation(self) -> pd.DataFrame:
        """Run the World3 simulation and return results.

        Returns:
            DataFrame containing simulation results
        """
        if self.world3 is None:
            print("Initializing model before simulation...")
            self.initialize_model()

        try:
            print("Running World3 simulation...")
            # Run simulation
            self.world3.run_world3()

            # Extract results into DataFrame
            print("Processing simulation results...")
            time_series = np.arange(self.start_time, self.stop_time + self.dt, self.dt)

            # Get all available variables
            vars_dict = {
                'population': self.world3.pop,
                'industrial_output': self.world3.io,
                'persistent_pollution_index': self.world3.ppol
            }

            self.results = pd.DataFrame(vars_dict, index=time_series)
            print("Simulation completed successfully.")
            return self.results

        except Exception as e:
            print(f"Error during simulation: {str(e)}")
            raise

    def get_variables(self) -> Dict[str, Any]:
        """Get all available variables in the model.

        Returns:
            Dictionary of variable names and their current values
        """
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