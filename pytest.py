"""Modified test for PyWorld3 population modification."""
from myworld3.models.base_model import BaseModel
import pandas as pd

def test_population():
    """Test population modification in World3."""
    print("Testing population scaling in World3...")

    # Create model instance with 8 billion target population
    model = BaseModel(
        start_time=1900,
        stop_time=2100,
        dt=0.5,
        target_population=8000  # 8 billion in millions
    )

    # Initialize and run model
    results = model.run_simulation()

    # Print population at key years
    print("\nPopulation at key years (millions):")
    for year in [1900, 1950, 2000, 2050, 2100]:
        idx = year
        pop = results.loc[idx, 'population']
        p1 = results.loc[idx, 'population_0_14']
        p2 = results.loc[idx, 'population_15_44']
        p3 = results.loc[idx, 'population_45_64']
        p4 = results.loc[idx, 'population_65_plus']

        print(f"\nYear {year}:")
        print(f"Total: {pop:.2f} million ({pop/1000:.2f} billion)")
        print(f"Age distribution:")
        print(f"  0-14:  {p1:.2f} million ({p1/pop*100:.1f}%)")
        print(f"  15-44: {p2:.2f} million ({p2/pop*100:.1f}%)")
        print(f"  45-64: {p3:.2f} million ({p3/pop*100:.1f}%)")
        print(f"  65+:   {p4:.2f} million ({p4/pop*100:.1f}%)")

if __name__ == '__main__':
    test_population()