def SMA(data, window):
    """  
    Compute the simple moving average (SMA) using a sliding window
    Args:
        data (list or 1d array): Sequence of numbers
        window (int): Size of the moving window
    Returns:
        list: the moving average values, with None for the first window
    """
    if window < 1:
        raise ValueError("Window size must be at least 1")
    
    averages = []
    for i in range(len(data)):
        if i + 1 < window:
            averages.append(None)
        else:
            window_slice = data[i - window + 1: i + 1]
            averages.append(sum(window_slice)/window)
    return averages
