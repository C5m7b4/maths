import numpy as np
import pandas as pd

def custom_acf(x, nlags):
    """
    Compute the (biased) autocorrelation function up to lag=nlags.
    
    Parameters:
      x      : 1D array-like (list, np.ndarray, or pd.Series) of length N
      nlags  : integer, maximum lag to compute (must be < N)
    
    Returns:
      acf_vals : np.ndarray of length (nlags + 1), where
                 acf_vals[k] = autocorrelation at lag k.
    """
    # Convert to numpy array (float) and compute length
    arr = np.asarray(x, dtype=float)
    N = len(arr)
    if nlags >= N:
        raise ValueError("nlags must be strictly less than the length of the series")
    
    # 1) Compute the mean, then center the series
    # to see more about centering the series, check out he notebook on centering_a_series.ipynb
    mu = arr.mean()
    y = arr - mu              # y_t = x_t - mu
    
    # 2) Precompute denominator = gamma(0) = (1/N)*sum(y_t^2)
    #    (Note: we’ll divide numerator by this at the end)
    gamma0 = (y * y).sum() / N
    if gamma0 == 0:
        # Perfectly constant series → all ACFs undefined except at lag 0
        acf_all = np.zeros(nlags + 1, dtype=float)
        acf_all[0] = 1.0
        return acf_all
    
    # 3) For each k from 0 to nlags, compute gamma(k)
    acf_vals = np.empty(nlags + 1, dtype=float)
    for k in range(nlags + 1):
        # Sum_{t=0..N-1-k} [ y[t] * y[t+k] ]
        numerator = np.dot(y[: N - k], y[k : N]) / N
        acf_vals[k] = numerator / gamma0
    
    return acf_vals
