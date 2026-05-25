import numpy as np
import pandas as pd
import os

def run_monte_carlo_simulation(csv_path, iterations, drainage_efficiency):
    """
    Simulates flood depth distributions using Monte Carlo simulation
    based on historical rainfall data from a CSV file.
    
    :param csv_path: Path to the historical data CSV
    :param iterations: Number of simulated weather scenarios
    :param drainage_efficiency: Drainage efficiency percentage (20-100)
    :return: Dictionary containing simulation results
    """
    print(f"Reading historical data from {os.path.basename(csv_path)}...")
    df = pd.read_csv(csv_path)
    
    # Extract historical rainfall data
    # Filter out 0 to properly calculate log-normal parameters
    historical_rainfall = df[df['Rainfall_mm'] > 0]['Rainfall_mm']
    
    # Calculate log-normal parameters from historical data
    mu = np.mean(np.log(historical_rainfall))
    sigma = np.std(np.log(historical_rainfall))
    
    base_rainfall_mean = np.mean(historical_rainfall)
    print(f"Historical Mean Rainfall: {base_rainfall_mean:.2f} mm")
    print(f"Running Monte Carlo Simulation with {iterations} iterations...")
    
    # Drainage capacity model (higher efficiency = more water drained)
    # Assuming max drainage capacity is 150 mm/hr at 100% efficiency
    drainage_capacity = (drainage_efficiency / 100.0) * 150 
    
    # Generate random rainfall data (log-normal distribution based on historical fit)
    simulated_rainfall = np.random.lognormal(mean=mu, sigma=sigma, size=iterations)
    
    # Calculate flood depths (simplified model)
    # Depth = k * max(0, rainfall - drainage_capacity)
    k = 0.02 # Conversion factor to meters
    flood_depths = k * np.maximum(0, simulated_rainfall - drainage_capacity)
    
    # Calculate probabilities for different depth thresholds
    thresholds = [0, 0.5, 1.0, 1.5, 2.0, 2.5]
    probabilities = {}
    
    for i in range(len(thresholds) - 1):
        count = np.sum((flood_depths >= thresholds[i]) & (flood_depths < thresholds[i+1]))
        probabilities[f"{thresholds[i]}-{thresholds[i+1]}m"] = (count / iterations) * 100
        
    count_max = np.sum(flood_depths >= thresholds[-1])
    probabilities[f">{thresholds[-1]}m"] = (count_max / iterations) * 100
    
    return {
        "historical_mean": base_rainfall_mean,
        "mean_depth": np.mean(flood_depths),
        "max_depth": np.max(flood_depths),
        "depth_distribution": probabilities
    }

if __name__ == "__main__":
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(current_dir, 'Flood_Prediction_NCR_Philippines.csv')
    
    if os.path.exists(csv_file_path):
        results = run_monte_carlo_simulation(
            csv_path=csv_file_path, 
            iterations=5000, 
            drainage_efficiency=65
        )
        
        print("\n=== Monte Carlo Simulation Results ===")
        print(f"Mean Flood Depth: {results['mean_depth']:.2f}m")
        print(f"Max Flood Depth:  {results['max_depth']:.2f}m")
        print("\nDepth Distribution Probabilities:")
        for range_str, prob in results['depth_distribution'].items():
            print(f"  {range_str}: {prob:>5.1f}%")
    else:
        print(f"Error: Could not find CSV file at {csv_file_path}")
