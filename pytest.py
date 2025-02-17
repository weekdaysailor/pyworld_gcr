"""Simple test for PyWorld3 population modification."""
from pyworld3 import World3
import numpy as np
import pandas as pd

def test_population():
    """Test population modification in World3."""
    print("Initializing World3 test...")

    # Create World3 instance with basic parameters
    world3 = World3(
        year_min=1900,
        year_max=2100,
        dt=0.5,
        pyear=1975,
        verbose=True
    )

    # Print available attributes before initialization
    print("\nAvailable attributes before initialization:")
    attrs = [attr for attr in dir(world3) if not attr.startswith('_')]
    print(f"Attributes: {attrs}")

    # Initialize the model
    print("\nInitializing World3 model...")
    world3.init_world3_constants()
    world3.init_world3_variables()

    # Initialize each subsystem
    print("\nInitializing subsystems...")
    # Population subsystem
    world3.init_population_constants()
    world3.init_population_variables()
    world3.set_population_table_functions()
    world3.set_population_delay_functions()

    # Capital subsystem
    world3.init_capital_constants()
    world3.init_capital_variables()
    world3.set_capital_table_functions()
    world3.set_capital_delay_functions()

    # Agriculture subsystem
    world3.init_agriculture_constants()
    world3.init_agriculture_variables()
    world3.set_agriculture_table_functions()
    world3.set_agriculture_delay_functions()

    # Pollution subsystem
    world3.init_pollution_constants()
    world3.init_pollution_variables()
    world3.set_pollution_table_functions()
    world3.set_pollution_delay_functions()

    # Resource subsystem
    world3.init_resource_constants()
    world3.init_resource_variables()
    world3.set_resource_table_functions()
    world3.set_resource_delay_functions()

    # Initialize exogenous inputs
    world3.init_exogenous_inputs()

    # Set global World3 functions
    print("\nSetting up World3 global functions...")
    world3.set_world3_table_functions()
    world3.set_world3_delay_functions()

    # Print available attributes after initialization
    print("\nAvailable attributes after initialization:")
    attrs = [attr for attr in dir(world3) if not attr.startswith('_')]
    print(f"Attributes: {attrs}")

    # Print initial population
    print(f"\nInitial population (before modification): {world3.pop[0]}")

    # Modify initial population (double it)
    world3.pop[0] *= 2
    print(f"Modified population: {world3.pop[0]}")

    try:
        print("\nRunning simulation...")
        world3.run_world3()

        # Create time series for results
        time_series = np.arange(1900, 2100 + 0.5, 0.5)

        # Extract population data
        results = pd.DataFrame({
            'population': world3.pop,
        }, index=time_series)

        print("\nSimulation Results:")
        print(f"Final population (2100): {results['population'].iloc[-1]}")
        print("\nPopulation at key years:")
        for year in [1900, 1950, 2000, 2050, 2100]:
            pop = results.loc[year, 'population']
            print(f"Year {year}: {pop:,.0f}")

    except Exception as e:
        print(f"\nError during simulation: {str(e)}")
        print("Current World3 attributes at error:")
        attrs = [attr for attr in dir(world3) if not attr.startswith('_')]
        print(f"Attributes: {attrs}")
        raise

if __name__ == '__main__':
    test_population()