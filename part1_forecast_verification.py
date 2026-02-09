"""
Part 1: Forecast Verification vs ERA5 (Europe, t2m)
Author: Abdu Alim Arlikhozhaev
Date: February 2026

This script compares two weather forecasting models (IFS and AIFS) against ERA5 reanalysis data
for 2-meter temperature over Europe. It computes MAE, RMSE, and R² metrics and visualizes
the results.

Requirements:
- xarray
- numpy
- matplotlib
- scipy
- cdsapi (for ERA5 download)
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings('ignore')

def load_forecast_files(ifs_path, aifs_path):
    """
    Load the two forecast files and return them as xarray datasets.
    
    Args:
        ifs_path: Path to IFS forecast file
        aifs_path: Path to AIFS forecast file
    
    Returns:
        Tuple of (ifs_dataset, aifs_dataset)
    """
    print("Loading forecast files...")
    ifs_ds = xr.open_dataset(ifs_path)
    aifs_ds = xr.open_dataset(aifs_path)
    
    print(f"IFS forecast loaded: {ifs_ds.dims}")
    print(f"AIFS forecast loaded: {aifs_ds.dims}")
    
    return ifs_ds, aifs_ds

def find_overlapping_times(ifs_ds, aifs_ds):
    """
    Find the forecast-valid times that exist in both datasets.
    """
    print("\nFinding overlapping forecast times...")
    
    # Get time coordinates from both datasets
    # Handle both 'time' and 'valid_time' coordinate names
    if 'time' in ifs_ds.coords:
        ifs_times = ifs_ds.time
    elif 'valid_time' in ifs_ds.coords:
        ifs_times = ifs_ds.valid_time
    else:
        raise ValueError("Could not find time coordinate in IFS dataset")
    
    if 'time' in aifs_ds.coords:
        aifs_times = aifs_ds.time
    elif 'valid_time' in aifs_ds.coords:
        aifs_times = aifs_ds.valid_time
    else:
        raise ValueError("Could not find time coordinate in AIFS dataset")
    
    # Convert to numpy arrays for comparison
    ifs_times_np = ifs_times.values
    aifs_times_np = aifs_times.values
    
    # Find intersection
    overlapping_times = np.intersect1d(ifs_times_np, aifs_times_np)
    
    print(f"Found {len(overlapping_times)} overlapping times")
    print(f"First time: {overlapping_times[0]}")
    print(f"Last time: {overlapping_times[-1]}")
    
    return overlapping_times

def download_era5_data(times, output_path='era5_data.nc'):
    """
    Download ERA5 reanalysis data for the specified times.
    
    This function creates a CDS API request to download 2m temperature data.
    You need to have a CDS account and API key configured.
    
    Args:
        times: Array of datetime objects
        output_path: Path to save the downloaded file
    
    Returns:
        Path to downloaded file
    """
    import cdsapi
    
    print("\nPreparing ERA5 download request...")
    
    # Convert times to dates and hours
    dates = sorted(set([np.datetime_as_string(t, unit='D') for t in times]))
    hours = sorted(set([f"{np.datetime64(t, 'h').astype(int) % 24:02d}:00" for t in times]))
    
    # Parse year and month from dates
    years = sorted(set([d[:4] for d in dates]))
    months = sorted(set([d[5:7] for d in dates]))
    days = sorted(set([d[8:10] for d in dates]))
    
    print(f"Years: {years}")
    print(f"Months: {months}")
    print(f"Days: {days}")
    print(f"Hours: {hours}")
    
    c = cdsapi.Client()
    
    request = {
        'product_type': 'reanalysis',
        'variable': '2m_temperature',
        'year': years,
        'month': months,
        'day': days,
        'time': hours,
        'area': [75, -15, 35, 40],  # North, West, South, East for Europe
        'format': 'netcdf',
    }
    
    print("Downloading ERA5 data... (this may take a few minutes)")
    c.retrieve('reanalysis-era5-single-levels', request, output_path)
    
    print(f"ERA5 data downloaded to {output_path}")
    return output_path

def compute_metrics(forecast, truth):
    """
    Compute MAE, RMSE, and R² between forecast and ground truth.
    
    Args:
        forecast: Forecast data (numpy array or xarray DataArray)
        truth: Ground truth data (numpy array or xarray DataArray)
    
    Returns:
        Dictionary with 'mae', 'rmse', 'r2' keys
    """
    # Flatten arrays for computation
    if hasattr(forecast, 'values'):
        forecast = forecast.values
    if hasattr(truth, 'values'):
        truth = truth.values
    
    # Remove NaN values
    mask = ~(np.isnan(forecast) | np.isnan(truth))
    forecast_clean = forecast[mask].flatten()
    truth_clean = truth[mask].flatten()
    
    # Compute metrics
    mae = np.mean(np.abs(forecast_clean - truth_clean))
    rmse = np.sqrt(np.mean((forecast_clean - truth_clean) ** 2))
    r2 = r2_score(truth_clean, forecast_clean)
    
    return {
        'mae': mae,
        'rmse': rmse,
        'r2': r2
    }

def verify_forecasts(ifs_ds, aifs_ds, era5_ds, overlapping_times):
    """
    Verify both forecasts against ERA5 for all overlapping times.
    
    Args:
        ifs_ds: IFS forecast dataset
        aifs_ds: AIFS forecast dataset
        era5_ds: ERA5 reanalysis dataset
        overlapping_times: Array of times to verify
    
    Returns:
        Dictionary with results for both models
    """
    print("\nComputing verification metrics...")
    
    results = {
        'times': [],
        'ifs': {'mae': [], 'rmse': [], 'r2': []},
        'aifs': {'mae': [], 'rmse': [], 'r2': []}
    }
    
    # Get variable names (adjust based on actual file structure)
    t2m_var = 't2m' if 't2m' in ifs_ds.data_vars else '2t'
    era5_var = 't2m' if 't2m' in era5_ds.data_vars else '2t'
    
    # Determine time coordinate name for each dataset
    ifs_time_coord = 'time' if 'time' in ifs_ds.coords else 'valid_time'
    aifs_time_coord = 'time' if 'time' in aifs_ds.coords else 'valid_time'
    era5_time_coord = 'time' if 'time' in era5_ds.coords else 'valid_time'
    
    for time in overlapping_times:
        print(f"Processing time: {time}")
        results['times'].append(time)
        
        # Extract data for this time (using correct coordinate name)
        ifs_t2m = ifs_ds[t2m_var].sel({ifs_time_coord: time})
        aifs_t2m = aifs_ds[t2m_var].sel({aifs_time_coord: time})
        era5_t2m = era5_ds[era5_var].sel({era5_time_coord: time}, method='nearest')
        
        # Ensure all datasets are on the same grid (interpolate if needed)
        # This is a simple approach - in production you might use more sophisticated methods
        if ifs_t2m.shape != era5_t2m.shape:
            era5_t2m = era5_t2m.interp_like(ifs_t2m)
        if aifs_t2m.shape != era5_t2m.shape:
            era5_t2m_aifs = era5_t2m.interp_like(aifs_t2m)
        else:
            era5_t2m_aifs = era5_t2m
        
        # Compute metrics for IFS
        ifs_metrics = compute_metrics(ifs_t2m, era5_t2m)
        results['ifs']['mae'].append(ifs_metrics['mae'])
        results['ifs']['rmse'].append(ifs_metrics['rmse'])
        results['ifs']['r2'].append(ifs_metrics['r2'])
        
        # Compute metrics for AIFS
        aifs_metrics = compute_metrics(aifs_t2m, era5_t2m_aifs)
        results['aifs']['mae'].append(aifs_metrics['mae'])
        results['aifs']['rmse'].append(aifs_metrics['rmse'])
        results['aifs']['r2'].append(aifs_metrics['r2'])
        
        print(f"  IFS  - MAE: {ifs_metrics['mae']:.2f}, RMSE: {ifs_metrics['rmse']:.2f}, R²: {ifs_metrics['r2']:.3f}")
        print(f"  AIFS - MAE: {aifs_metrics['mae']:.2f}, RMSE: {aifs_metrics['rmse']:.2f}, R²: {aifs_metrics['r2']:.3f}")
    
    return results

def plot_results(results, output_path='forecast_verification.png'):
    """
    Create visualization of verification metrics over time.
    
    Args:
        results: Dictionary containing verification results
        output_path: Path to save the plot
    """
    print("\nCreating verification plots...")
    
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    times = results['times']
    
    # MAE plot
    axes[0].plot(times, results['ifs']['mae'], 'o-', label='IFS', linewidth=2, markersize=6)
    axes[0].plot(times, results['aifs']['mae'], 's-', label='AIFS', linewidth=2, markersize=6)
    axes[0].set_ylabel('MAE (K)', fontsize=12)
    axes[0].set_title('Mean Absolute Error vs ERA5', fontsize=14, fontweight='bold')
    axes[0].legend(fontsize=11)
    axes[0].grid(True, alpha=0.3)
    
    # RMSE plot
    axes[1].plot(times, results['ifs']['rmse'], 'o-', label='IFS', linewidth=2, markersize=6)
    axes[1].plot(times, results['aifs']['rmse'], 's-', label='AIFS', linewidth=2, markersize=6)
    axes[1].set_ylabel('RMSE (K)', fontsize=12)
    axes[1].set_title('Root Mean Square Error vs ERA5', fontsize=14, fontweight='bold')
    axes[1].legend(fontsize=11)
    axes[1].grid(True, alpha=0.3)
    
    # R² plot
    axes[2].plot(times, results['ifs']['r2'], 'o-', label='IFS', linewidth=2, markersize=6)
    axes[2].plot(times, results['aifs']['r2'], 's-', label='AIFS', linewidth=2, markersize=6)
    axes[2].set_ylabel('R²', fontsize=12)
    axes[2].set_xlabel('Forecast Valid Time', fontsize=12)
    axes[2].set_title('Coefficient of Determination vs ERA5', fontsize=14, fontweight='bold')
    axes[2].legend(fontsize=11)
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved to {output_path}")
    
    return fig

def generate_summary_statistics(results):
    """
    Generate summary statistics for the verification results.
    
    Args:
        results: Dictionary containing verification results
    
    Returns:
        Dictionary with summary statistics
    """
    summary = {
        'ifs': {
            'mae_mean': np.mean(results['ifs']['mae']),
            'mae_std': np.std(results['ifs']['mae']),
            'rmse_mean': np.mean(results['ifs']['rmse']),
            'rmse_std': np.std(results['ifs']['rmse']),
            'r2_mean': np.mean(results['ifs']['r2']),
            'r2_std': np.std(results['ifs']['r2']),
        },
        'aifs': {
            'mae_mean': np.mean(results['aifs']['mae']),
            'mae_std': np.std(results['aifs']['mae']),
            'rmse_mean': np.mean(results['aifs']['rmse']),
            'rmse_std': np.std(results['aifs']['rmse']),
            'r2_mean': np.mean(results['aifs']['r2']),
            'r2_std': np.std(results['aifs']['r2']),
        }
    }
    
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    print("\nIFS Forecast:")
    print(f"  MAE:  {summary['ifs']['mae_mean']:.2f} ± {summary['ifs']['mae_std']:.2f} K")
    print(f"  RMSE: {summary['ifs']['rmse_mean']:.2f} ± {summary['ifs']['rmse_std']:.2f} K")
    print(f"  R²:   {summary['ifs']['r2_mean']:.3f} ± {summary['ifs']['r2_std']:.3f}")
    
    print("\nAIFS Forecast:")
    print(f"  MAE:  {summary['aifs']['mae_mean']:.2f} ± {summary['aifs']['mae_std']:.2f} K")
    print(f"  RMSE: {summary['aifs']['rmse_mean']:.2f} ± {summary['aifs']['rmse_std']:.2f} K")
    print(f"  R²:   {summary['aifs']['r2_mean']:.3f} ± {summary['aifs']['r2_std']:.3f}")
    print("="*60)
    
    return summary

def main():
    """
    Main execution function for Part 1.
    """
    print("="*60)
    print("SORANO AI INTERNSHIP - PART 1: FORECAST VERIFICATION")
    print("="*60)
    
    # File paths - UPDATE THESE with actual file locations
    IFS_PATH = 'IFS_forecast_europe.nc'
    AIFS_PATH = 'AIFS_forecast_europe.nc'
    ERA5_PATH = 'era5_data.nc'
    
    # Step 1: Load forecast files
    ifs_ds, aifs_ds = load_forecast_files(IFS_PATH, AIFS_PATH)
    
    # Step 2: Find overlapping times
    overlapping_times = find_overlapping_times(ifs_ds, aifs_ds)
    
    # Step 3: Download ERA5 data (uncomment when ready)
    # Note: This requires CDS API setup. See instructions below.
    # era5_path = download_era5_data(overlapping_times, ERA5_PATH)
    
    # For testing, if ERA5 is already downloaded:
    print(f"\nLoading ERA5 data from {ERA5_PATH}...")
    era5_ds = xr.open_dataset(ERA5_PATH)
    
    # Step 4: Verify forecasts
    results = verify_forecasts(ifs_ds, aifs_ds, era5_ds, overlapping_times)
    
    # Step 5: Plot results
    plot_results(results, 'forecast_verification.png')
    
    # Step 6: Generate summary statistics
    summary = generate_summary_statistics(results)
    
    # Close datasets
    ifs_ds.close()
    aifs_ds.close()
    era5_ds.close()
    
    print("\n✓ Analysis complete!")
    print("\nOutputs:")
    print("  - forecast_verification.png (visualization)")
    print("  - Metrics computed for all overlapping times")

if __name__ == "__main__":
    main()
