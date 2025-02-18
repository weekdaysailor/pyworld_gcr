"""Base model class for World3 simulations."""
from typing import Dict, Any, Optional, Union
import numpy as np
import pandas as pd
from pyworld3 import World3

class BaseModel:
    """Base class for World3-based models."""

    def __init__(self, start_time: int = 1900, stop_time: int = 2100, dt: float = 0.5,
                 target_population: Optional[float] = 0):
        """Initialize the base model."""
        self.start_time = start_time
        self.stop_time = stop_time
        self.dt = dt
        self.target_population = target_population
        self.world3: Optional[World3] = None
        self.results: Optional[pd.DataFrame] = None
        self.base_intensity = 2.5  # Base CO2e intensity per unit of industrial output
        self.tech_improvement_rate = 0.01  # 1% annual improvement in base technology

        # Historical CO2 data (ppm) - Combination of ice core data and Mauna Loa measurements
        # Pre-1958 values are from ice core data, post-1958 from Mauna Loa
        self.historical_co2 = {
            1900: 296.3,  # Ice core derived
            1910: 299.4,
            1920: 302.9,
            1930: 306.8,
            1940: 310.5,
            1950: 311.3,
            1958: 315.39,  # Start of Mauna Loa measurements
            1960: 316.91,
            1965: 320.04,
            1970: 325.68,
            1975: 331.08,
            1980: 338.91,
            1985: 346.35,
            1990: 354.39,
            1995: 360.80,
            2000: 369.55,
            2005: 379.80,
            2010: 389.90,
            2015: 400.83,
            2020: 414.72,
            2025: 421.50  # Recent measurements
        }

        # Natural carbon cycle parameters
        self.natural_carbon_uptake = 0.0167  # ~1.67% of excess CO2 absorbed annually by natural sinks
        self.residence_time = 100  # Minimum sequestration time in years for XCC credits

    def calculate_emission_intensity(self, year: int, industrial_output: float) -> float:
        """Calculate emission intensity factor considering technological improvements."""
        years_passed = year - self.start_time
        # Technological improvement reduces base intensity over time
        tech_factor = (1 - self.tech_improvement_rate) ** years_passed
        # Scale factor based on industrial output (economies of scale)
        scale_factor = 1.0 + (np.log(industrial_output / 100) * 0.1)
        return float(self.base_intensity * tech_factor * scale_factor)

    def calculate_co2e(self, year: int, industrial_output: float, pollution_index: float) -> Dict[str, float]:
        """Calculate CO2e emissions components and net emissions."""
        try:
            # Get base intensity adjusted for technology and scale
            intensity = self.calculate_emission_intensity(year, industrial_output)

            # Calculate gross emissions from industrial activity
            gross_emissions = industrial_output * intensity

            # Additional emissions from pollution feedback
            pollution_multiplier = 1.0 + (pollution_index * 0.2)
            total_emissions = gross_emissions * pollution_multiplier

            # Calculate natural carbon uptake
            natural_uptake = total_emissions * self.natural_carbon_uptake

            # Apply historical calibration for pre-2025 emissions
            if year <= 2025:
                nearest_historical = min(self.historical_co2.keys(),
                                          key=lambda x: abs(x - year))
                historical_factor = self.historical_co2[nearest_historical] / self.historical_co2[1900]
                total_emissions *= historical_factor
                natural_uptake *= historical_factor

            # Calculate net emissions (no XCC sequestration in base model)
            net_emissions = total_emissions - natural_uptake

            return {
                'gross_emissions': float(total_emissions),
                'natural_uptake': float(natural_uptake),
                'net_emissions': float(net_emissions),
                'emission_intensity': float(intensity)
            }
        except Exception as e:
            print(f"Error calculating CO2e: {str(e)}")
            return {
                'gross_emissions': 0.0,
                'natural_uptake': 0.0,
                'net_emissions': 0.0,
                'emission_intensity': self.base_intensity
            }

    def scale_population(self) -> None:
        """Scale population and related factors to match target population while maintaining balance."""
        if self.target_population is None or self.world3 is None:
            return

        # Calculate current total from cohorts
        current_total = (self.world3.p1i + self.world3.p2i +
                         self.world3.p3i + self.world3.p4i)

        print(f"\nInitial state before scaling:")
        print(f"Population:        {current_total:.2f} million")
        print(f"Industrial Output: {self.world3.ici:.2f}")
        print(f"Food Production:   {self.world3.ali:.2f}")
        print(f"Service Output:    {self.world3.sci:.2f}")

        # If target population is 0, keep original values
        if self.target_population == 0:
            print("\nSkipping population scaling (target = 0)")
            return

        # Calculate scaling factor with safety check
        scaling_factor = float(self.target_population) / float(current_total) if current_total > 0 else 1.0

        print(f"\nScaling system by factor: {scaling_factor:.4f}")

        # Scale population cohorts
        self.world3.p1i *= scaling_factor   # 0-14 years
        self.world3.p2i *= scaling_factor   # 15-44 years
        self.world3.p3i *= scaling_factor   # 45-64 years
        self.world3.p4i *= scaling_factor   # 65+ years

        # Scale industrial and agricultural systems
        self.world3.ici *= scaling_factor * 0.9   # Industrial capital
        self.world3.ali *= scaling_factor * 0.95  # Arable land
        self.world3.sfpc *= 1.0                   # Food per capita remains constant

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
        """Run World3 simulation and calculate atmospheric CO2."""
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
                'food_per_capita': self.world3.sfpc,
                'service_output_per_capita': self.world3.sopc,
                'resources': self.world3.nrfr,
                'life_expectancy': self.world3.le
            }

            # Create initial DataFrame
            self.results = pd.DataFrame(vars_dict, index=time_series)

            # Initialize emissions-related columns
            self.results['gross_emissions'] = 0.0
            self.results['natural_uptake'] = 0.0
            self.results['net_emissions'] = 0.0
            self.results['emission_intensity'] = 0.0
            self.results['xcc_sequestration'] = 0.0  # Will remain 0 for base model
            self.results['atmospheric_co2'] = 0.0

            # First calculate emissions for each timestep
            for time in time_series:
                emissions_data = self.calculate_co2e(
                    int(time),
                    self.results.loc[time, 'industrial_output'],
                    self.results.loc[time, 'persistent_pollution_index']
                )

                # Store all emission components
                for key, value in emissions_data.items():
                    self.results.loc[time, key] = value

            # Now calculate cumulative emissions and atmospheric CO2
            cumulative_emissions = self.results['net_emissions'].cumsum()

            # Calculate atmospheric CO2 for each timestep
            for time in time_series:
                self.results.loc[time, 'atmospheric_co2'] = self.calculate_atmospheric_co2(
                    int(time),
                    cumulative_emissions[time]
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

    def calculate_atmospheric_co2(self, year: int, cumulative_emissions: float) -> float:
        """Calculate atmospheric CO2 concentration in ppm."""
        try:
            # For historical period (up to 2025), use exponential interpolation
            if year <= 2025:
                # Find the two closest years
                years = sorted(self.historical_co2.keys())
                lower_year = max([y for y in years if y <= year])
                upper_year = min([y for y in years if y >= year])

                # If exact year exists, return that value
                if lower_year == upper_year:
                    return self.historical_co2[year]

                # Get CO2 values for bounds
                lower_co2 = self.historical_co2[lower_year]
                upper_co2 = self.historical_co2[upper_year]

                # Calculate time fraction
                time_span = upper_year - lower_year
                time_progress = year - lower_year

                # Use exponential interpolation for smoother curve
                # ln(CO2) = a + bt, where t is time
                if lower_co2 > 0 and upper_co2 > 0:
                    a = np.log(lower_co2)
                    b = (np.log(upper_co2) - np.log(lower_co2)) / time_span
                    return float(np.exp(a + b * time_progress))

                return lower_co2 + (upper_co2 - lower_co2) * (time_progress / time_span)

            # For future projections (after 2025)
            # Convert cumulative emissions to CO2 concentration increase
            # Using conversion factors:
            # 1 GtC ≈ 0.47 ppm CO2 in atmosphere
            # First convert Mt CO2e to GtC (divide by 3667 for molecular weight conversion)
            gtc_emissions = cumulative_emissions / 3667 / 1000

            # Calculate ppm increase from 2025 baseline
            ppm_increase = gtc_emissions * 0.47

            # Add to 2025 baseline (last historical value)
            return self.historical_co2[2025] + float(ppm_increase)

        except Exception as e:
            print(f"Error calculating atmospheric CO2: {str(e)}")
            return self.historical_co2[1900]  # fallback to 1900 value