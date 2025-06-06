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
        # CI is degenerate at 1 for k=0, at +1 for others (Or you could set 1.96/sqrt(N)
        ci_lower = np.zeros(nlags + 1)
        ci_upper = np.zeros(nlags + 1)
        ci_lower[0] = 1.0
        ci_upper[0] = 1.0
        # for k in range(1, nlags + 1):
        #     ci_lower[k] = -1.0
        #     ci_upper[k] = 1.0
        return acf_all, ci_lower, ci_upper
    
    # 3) For each k from 0 to nlags, compute gamma(k)
    acf_vals = np.empty(nlags + 1, dtype=float)
    for k in range(nlags + 1):
        # Sum_{t=0..N-1-k} [ y[t] * y[t+k] ]
        numerator = np.dot(y[: N - k], y[k : N]) / N
        acf_vals[k] = numerator / gamma0

    # 4) Now compute Bartlett’s‐formula CI for each lag > 0
    ci_lower = np.empty(nlags + 1, dtype=float)
    ci_upper = np.empty(nlags + 1, dtype=float)

    # Lag 0 is exactly ρ(0)=1; we can clamp CI to [1,1]
    ci_lower[0] = ci_upper[0] = 1.0        

    # For k ≥ 1, use Var(ρ̂(k)) ≈ [1 + 2 ∑_{j=1..(k-1)} ρ̂(j)^2] / N
    for k in range(1, nlags + 1):
        sum_of_squares = np.sum(acf_vals[1:k]**2)  # sum_{j=1..(k-1)} ρ̂(j)²
        var_rk = (1 + 2 * sum_of_squares) / N
        stderr_k = np.sqrt(var_rk)
        delta = 1.96 * stderr_k

        ci_lower[k] = acf_vals[k] - delta
        ci_upper[k] = acf_vals[k] + delta
    
    return acf_vals, ci_lower, ci_upper
