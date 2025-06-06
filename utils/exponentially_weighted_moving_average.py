import pandas as pd

def EWMA(data, alpha=0.1):
    """
    Calculate the Exponentially Weighted Moving Average (EWMA) of a given data series.

    Parameters:
    data (list or pd.Series): The input data series.
    alpha (float): The smoothing factor, between 0 and 1. Default is 0.1.

    Returns:
    list: The EWMA of the input data.
    """
    if not isinstance(data, (list, pd.Series)):
        raise ValueError("Input data must be a list or a pandas Series.")
    
    ewma = []
    for i, value in enumerate(data):
        if i == 0:
            ewma.append(value)
        else:
            ewma.append(alpha * value + (1 - alpha) * ewma[i - 1])
    
    return ewma