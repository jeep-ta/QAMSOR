# Quantitative Models: FloodRisk Research

This folder contains the Python scripts and data used for the quantitative modeling portion of the FloodRisk Research project.

## Files Overview
- `monte_carlo_simulation.py`: Simulates flood depth distributions using a stochastic Monte Carlo approach.
- `linear_programming_routing.py`: Optimizes evacuation routing using deterministic Linear Programming.
- `Flood_Prediction_NCR_Philippines.csv`: Historical dataset containing daily flood statistics (rainfall, water level, soil moisture, etc.) across the NCR region.
- `requirements.txt`: Python package dependencies needed to execute the scripts.

---

## Setup Instructions

Install the necessary dependencies to run the scripts. Python 3.8+ is recommended.

```bash
pip install -r requirements.txt
```

---

## 1. Monte Carlo Simulation (`monte_carlo_simulation.py`)

This script models the probability of various flood depths based on historical rainfall data.

**How it works:**
- Reads the historical rainfall data from the provided CSV file (ignoring days with `0 mm` of rain to ensure a proper fit).
- Calculates the true mean and standard deviation of the log-normalized rainfall.
- Simulates thousands of weather scenarios (default: `5000` iterations) drawing from a log-normal distribution.
- Subtracts a hypothetical drainage capacity to determine the resulting flood depths.
- Outputs the probabilities of flood depths falling into different severity tiers (e.g., `0-0.5m`, `0.5-1.0m`, etc.).

**To run:**
```bash
python monte_carlo_simulation.py
```

---

## 2. Linear Programming Routing (`linear_programming_routing.py`)

This script uses deterministic linear programming to find the mathematically optimal assignment of evacuees from high-risk locations to designated shelters.

**How it works:**
- Reads the historical dataset to identify the active locations (Quezon City, Marikina, Manila, Pasig).
- Determines realistic evacuee "demand" by aggregating the historical `FloodOccurrence` events per location (assuming an average number of evacuees per historical flood event).
- Generates a generic distance matrix between these origin locations and available shelters.
- Formulates a constrained mathematical optimization problem where the objective is to **minimize the total travel distance** while ensuring:
  - All evacuee demands are met.
  - Shelter capacities are not exceeded.
- Solves the problem using the `highs` solver from SciPy and outputs the optimal routing allocation and total objective distance.

**To run:**
```bash
python linear_programming_routing.py
```
