"""Modified test for PyWorld3 population modification."""
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
        pyear=1900,
        verbose=True
    )

    print("\nInitializing core World3 components...")
    # Initialize all constants first
    world3.init_world3_constants()
    world3.init_population_constants()
    world3.init_capital_constants()
    world3.init_agriculture_constants()
    world3.init_pollution_constants()
    world3.init_resource_constants()

    # Calculate scaling factor from default 1900 population
    desired_pop = 8000  # 8 billion (in millions)
    base_pop = 1650  # Default 1900 population in World3 (millions)
    scaling_factor = desired_pop / base_pop

    print(f"\nScaling factor: {scaling_factor:.4f}")
    print("Initial values before scaling:")
    print(f"p1i: {world3.p1i:.2f}")
    print(f"p2i: {world3.p2i:.2f}")
    print(f"p3i: {world3.p3i:.2f}")
    print(f"p4i: {world3.p4i:.2f}")

    # Scale initial population-related parameters
    print("\nScaling population parameters...")
    world3.p1i *= scaling_factor  # Initial 0-14 population
    world3.p2i *= scaling_factor  # Initial 15-44 population
    world3.p3i *= scaling_factor  # Initial 45-64 population
    world3.p4i *= scaling_factor  # Initial 65+ population

    print("\nValues after scaling:")
    print(f"p1i: {world3.p1i:.2f}")
    print(f"p2i: {world3.p2i:.2f}")
    print(f"p3i: {world3.p3i:.2f}")
    print(f"p4i: {world3.p4i:.2f}")
    print(f"Total: {world3.p1i + world3.p2i + world3.p3i + world3.p4i:.2f}")

    # Initialize all variables after scaling
    print("\nInitializing all subsystem variables...")
    world3.init_population_variables()
    world3.init_capital_variables()
    world3.init_agriculture_variables()
    world3.init_pollution_variables()
    world3.init_resource_variables()

    print("\nPopulation values after variable initialization:")
    print(f"p1[0]: {world3.p1[0]:.2f}")
    print(f"p2[0]: {world3.p2[0]:.2f}")
    print(f"p3[0]: {world3.p3[0]:.2f}")
    print(f"p4[0]: {world3.p4[0]:.2f}")
    print(f"pop[0]: {world3.pop[0]:.2f}")

    # Set up all subsystem functions
    print("\nSetting up model functions...")
    world3.set_population_table_functions()
    world3.set_capital_table_functions()
    world3.set_agriculture_table_functions()
    world3.set_pollution_table_functions()
    world3.set_resource_table_functions()

    world3.set_population_delay_functions()
    world3.set_capital_delay_functions()
    world3.set_agriculture_delay_functions()
    world3.set_pollution_delay_functions()
    world3.set_resource_delay_functions()

    print("\nFinal population values before simulation:")
    print(f"Total population: {world3.pop[0]:.2f}")
    print(f"Ages 0-14:  {world3.p1[0]:.2f}")
    print(f"Ages 15-44: {world3.p2[0]:.2f}")
    print(f"Ages 45-64: {world3.p3[0]:.2f}")
    print(f"Ages 65+:   {world3.p4[0]:.2f}")

    try:
        print("\nRunning simulation...")
        world3.run_world3()

        # Create time series for results
        time_series = np.arange(1900, 2100 + 0.5, 0.5)

        # Store results
        results = pd.DataFrame({
            'year': time_series,
            'population': world3.pop,
            'p1': world3.p1,
            'p2': world3.p2,
            'p3': world3.p3,
            'p4': world3.p4
        })

        print("\nSimulation Results:")
        print("\nPopulation at key years (millions):")
        for year in [1900, 1950, 2000, 2050, 2100]:
            idx = results[results['year'] == year].index[0]
            pop = results.loc[idx, 'population']
            p1 = results.loc[idx, 'p1']
            p2 = results.loc[idx, 'p2']
            p3 = results.loc[idx, 'p3']
            p4 = results.loc[idx, 'p4']
            print(f"\nYear {year}:")
            print(f"Total: {pop:.2f} million ({pop/1000:.2f} billion)")
            print(f"Age distribution:")
            print(f"  0-14:  {p1:.2f} million ({p1/pop*100:.1f}%)")
            print(f"  15-44: {p2:.2f} million ({p2/pop*100:.1f}%)")
            print(f"  45-64: {p3:.2f} million ({p3/pop*100:.1f}%)")
            print(f"  65+:   {p4:.2f} million ({p4/pop*100:.1f}%)")

    except Exception as e:
        print(f"\nError during simulation: {str(e)}")
        raise

if __name__ == '__main__':
    test_population()