import pandas as pd

def fill_missing_dates(ds, date_col, sales_col, start_date, end_date, fill_value=0.01):
    """
    Adds missing dates to the dataframe with zero sales.

    Parameters:
        ds (pd.DataFrame): Original dataframe.
        date_col (str): Column name for the date.
        sales_col (str): Column name for the sales value.
        start_date (str or pd.Timestamp): Start of expected date range.
        end_date (str or pd.Timestamp): End of expected date range.

    Returns:
        pd.DataFrame: DataFrame with missing dates filled and sales set to zero.
    """
    # Ensure datetime
    ds[date_col] = pd.to_datetime(ds[date_col])

    # Create complete date range
    full_range = pd.DataFrame({date_col: pd.date_range(start=start_date, end=end_date)})

    # Merge on date to find & fill missing ones
    merged = pd.merge(full_range, ds, on=date_col, how='left')

    # Fill NaN sales with 0
    merged[sales_col] = merged[sales_col].fillna(fill_value)

    return merged.sort_values(date_col)
