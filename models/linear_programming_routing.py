import pandas as pd
from scipy.optimize import linprog
import numpy as np
import os

def run_evacuation_lp(csv_path, demand_multiplier=1.0):
    """
    Optimizes evacuation routing using Linear Programming.
    Reads historical flood data to determine evacuee demands per location.
    
    :param csv_path: Path to the historical data CSV
    :param demand_multiplier: Multiplier for evacuee demands
    """
    print(f"Reading historical data from {os.path.basename(csv_path)}...")
    df = pd.read_csv(csv_path)
    
    print("Formulating Linear Programming Evacuation Model...")
    
    # Extract unique locations from the CSV
    # E.g., ['Quezon City', 'Marikina', 'Manila', 'Pasig']
    locations = df['Location'].unique().tolist()
    
    # Calculate base demand from historical flood occurrences
    # Assuming each historical flood occurrence requires evacuating ~50 people on average
    base_demands = []
    for loc in locations:
        flood_count = df[df['Location'] == loc]['FloodOccurrence'].sum()
        demand = max(100, int(flood_count * 50)) # Ensure at least 100 evacuees
        base_demands.append(demand)
        
    demands = np.floor(np.array(base_demands) * demand_multiplier)
    
    # Shelters (Destinations): Generic shelters for the NCR context
    shelters = ['NCR Central Shelter', 'East Valley Gym']
    
    # Shelter capacities (dynamically scale based on total demand so problem is feasible)
    total_demand = sum(demands)
    capacities = [int(total_demand * 0.6), int(total_demand * 0.6)] 
    
    # Distances (km) from each Location to each Shelter (Mocked based on generic layout)
    # Rows: Locations (n)
    # Cols: Shelters (2)
    # Creating a random but consistent distance matrix based on the number of locations
    np.random.seed(42) # For reproducible mock distances
    distances = np.random.uniform(2.0, 15.0, size=(len(locations), len(shelters)))
    
    # Flatten distance matrix to form the objective function coefficients
    c = distances.flatten()
    
    # Inequality constraints (Shelter capacities: sum(x_ij for i) <= Capacity_j)
    A_ub = np.zeros((len(shelters), len(locations) * len(shelters)))
    for j in range(len(shelters)):
        for i in range(len(locations)):
            A_ub[j, i * len(shelters) + j] = 1
            
    b_ub = capacities
    
    # Equality constraints (Evacuee demands: sum(x_ij for j) == Demand_i)
    A_eq = np.zeros((len(locations), len(locations) * len(shelters)))
    for i in range(len(locations)):
        for j in range(len(shelters)):
            A_eq[i, i * len(shelters) + j] = 1
            
    b_eq = demands
    
    # Bounds for variables (x_ij >= 0)
    bounds = [(0, None) for _ in range(len(c))]
    
    # Solve LP
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    
    if res.success:
        allocation = res.x.reshape((len(locations), len(shelters)))
        return {
            "status": "Optimal",
            "total_distance": res.fun,
            "allocation": allocation,
            "locations": locations,
            "shelters": shelters,
            "demands": demands
        }
    else:
        return {
            "status": "Infeasible",
            "message": "Shelter capacity exceeded or problem unsolvable."
        }

if __name__ == "__main__":
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(current_dir, 'Flood_Prediction_NCR_Philippines.csv')
    
    if os.path.exists(csv_file_path):
        result = run_evacuation_lp(csv_path=csv_file_path, demand_multiplier=1.2)
        
        print("\n=== Linear Programming Optimization Results ===")
        print(f"Solver Status: {result['status']}")
        
        if result['status'] == 'Optimal':
            print(f"Total Objective Distance: {result['total_distance']:.1f} km")
            print("\nEvacuee Demands Derived from Historical Data:")
            for i, loc in enumerate(result['locations']):
                print(f"  {loc:15}: {int(result['demands'][i])} evacuees")
                
            print("\nOptimal Routing Allocation (Evacuees):")
            for i, b in enumerate(result['locations']):
                for j, s in enumerate(result['shelters']):
                    count = result['allocation'][i][j]
                    if count > 0:
                        print(f"  [Route] {b:15} -> {s:20} : {int(count):>4} evacuees")
    else:
        print(f"Error: Could not find CSV file at {csv_file_path}")
