from math import nan
import pandas as pd

# v1
# def custom_diff(series):
#     diffs = [nan]
#     for t in range(1, len(series)):
#         diffs.append(series[t] - series[t - 1])
#     return diffs



# v2
# 😎 this way you can get back a pandas Series with the same index as the input or a list if the input is a list
def custom_diff(series):
    if not isinstance(series, (list, pd.Series)):
        raise TypeError("Input must be a list or pandas Series")

    is_series = isinstance(series, pd.Series)
    values = series.values if is_series else series

    diffs = [nan]
    for t in range(1, len(values)):
        diffs.append(values[t] - values[t - 1])

    if is_series:
        return pd.Series(diffs, index=series.index)
    return diffs