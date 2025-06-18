import numpy as np

def custom_rolling_mean(series, window, min_periods=1):
    """
    Computes a rolling mean after the length of the rolling window is >= min_periods and >= window size.

    Parameters:
    - series: array-like numeric data
    - window: number of trailing points to use
    - min_periods: min required for mean (default = window)

    Returns:
    - Array of rolling mean values
    """
    if min_periods is None:
        min_periods = window

    result = []
    for i in range(len(series)):
        start = max(0, i - window + 1)
        window_vals = series[start:i+1]

        if len(window_vals) >= min_periods and len(window_vals) >= window:
            result.append(np.mean(window_vals))
        else:
            result.append(np.nan)
    return np.array(result)