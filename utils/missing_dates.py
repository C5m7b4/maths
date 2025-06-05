import pandas as pd

def find_missing_dates(ds, date_col, start_date, end_date):
    """
    Checks for missing dates in a dataframe.

    Parameters:
        ds (pd.DataFrame): Your dataset.
        date_col (str): The name of the date column.
        start_date (str or pd.Timestamp): Start of the expected date range.
        end_date (str or pd.Timestamp): End of the expected date range.

        you can do ds['sale_date'].min() and ds['sale_date'].max() to get the range.

    Returns:
        List[pd.Timestamp]: A list of missing dates.
    """
    # Ensure datetime
    ds[date_col] = pd.to_datetime(ds[date_col])
    
    # Create full range of dates
    full_range = pd.date_range(start=start_date, end=end_date, freq='D')

    # Get unique dates in the dataset
    present_dates = pd.to_datetime(ds[date_col].dropna().unique())

    # Identify missing dates
    missing = sorted(set(full_range) - set(present_dates))

    return missing


