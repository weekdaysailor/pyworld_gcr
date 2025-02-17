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
        self.world3 = World3(
            start_time=self.start_time,
            stop_time=self.stop_time,
            dt=self.dt
        )
        
    def run_simulation(self) -> pd.DataFrame:
        """Run the World3 simulation and return results.
        
        Returns:
            DataFrame containing simulation results
        """
        if self.world3 is None:
            self.initialize_model()
            
        self.world3.run_simulation()
        self.results = pd.DataFrame(
            self.world3.results,
            index=self.world3.t
        )
        return self.results
    
    def get_variables(self) -> Dict[str, Any]:
        """Get all available variables in the model.
        
        Returns:
            Dictionary of variable names and their current values
        """
        if self.world3 is None:
            return {}
        return {
            var: getattr(self.world3, var)
            for var in dir(self.world3)
            if not var.startswith('_') and not callable(getattr(self.world3, var))
        }
