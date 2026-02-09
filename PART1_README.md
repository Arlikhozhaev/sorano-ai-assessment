# Part 1: Forecast Verification - Setup Guide

## What This Does?

This script compares two AI weather models (IFS and AIFS) against real-world ERA5 data to see which one is more accurate for predicting 2-meter temperature over Europe.

## Setup

### 1. Install Python Packages
```bash

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # on Windows

# Install the dependencies
pip install xarray netCDF4 numpy matplotlib scipy scikit-learn cdsapi
```

### 2. Set Up CDS API (for downloading ERA5 data)

1. Create account at https://cds.climate.copernicus.eu/
2. Get your API credentials:
   - Login → Click your name → User profile
   - Copy your UID and API Key
3. Create `~/.cdsapirc` file (in your home directory):
```
   url: https://cds.climate.copernicus.eu/api
   key: YOUR_UID:YOUR_API_KEY
```

## How to Run?

### Step 1: Get the forecast files
Place `IFS_forecast_europe.nc` and `AIFS_forecast_europe.nc` in the same folder as the script.

### Step 2: Run it
```bash
python part1_forecast_verification.py
```

Then the script will:
1. Load both forecast files
2. Find times that exist in both files
3. Download matching ERA5 data from CDS
4. Calculate error metrics for each time
5. Create a visualization
6. Show summary statistics

### Step 3: Check the results
- Console shows metrics for each time step
- `forecast_verification.png` shows the comparison plots
- Summary statistics show overall performance

## Understanding the Metrics

**MAE (Mean Absolute Error)**
- Average size of errors
- Units: Kelvin (K)
- Lower = better

**RMSE (Root Mean Square Error)**
- Like MAE but penalizes big errors more
- Units: Kelvin (K)
- Lower = better

**R² (Coefficient of Determination)**
- How well the forecast matches the pattern
- Range: 0 to 1
- Higher = better (1 is perfect)

## Common Issues

**ERA5 download is slow**
- This is normal - can take 5-30 minutes
- CDS will show your queue position
- Alternative: Download manually from the website

**Variable name errors**
- Different files sometimes use different names ('t2m' vs '2t')
- The script tries to detect this automatically
- If it fails, check the file structure with:
```python
  import xarray as xr
  print(xr.open_dataset('IFS_forecast_europe.nc'))
```

**Grid mismatch**
- The script handles this automatically with interpolation
- ERA5 has higher resolution and gets interpolated to match the forecast grid

## Expected Results

Good forecasts typically show:
- MAE: 1-3 K
- RMSE: 2-4 K
- R²: 0.85-0.95

The actual values will depend on the forecast period and weather conditions.

## Notes

- All temperatures are in Kelvin
- Times are in UTC
- Coverage: Europe (roughly 35°N-75°N, 15°W-40°E)
- The script handles missing values automatically

---

Built for SoranoAI Technical Assessment - February 2026