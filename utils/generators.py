import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_fake_time_series(num_days, end_date=None):
    """
    Generate a fake daily time series of length 'num_days'

    Parameters
    -----------
    num_days: int
        The number of days for which to generate the time series.
    end_date: str or datetime.date
        The last day in the series. If None, use todays date
        Can be a "YYYY-MM-Dd" string or a datetime.date object

    Returns
    -----------
    pd.DataFrame
        A DataFrame indexed by daily dates (no missing dates), with two columns:
        - 'sale_date': the date of the sale
        - 'sales': amount of sales on that date, randomly generated
    """

    # determine the end date
    if end_date is None:
        end = datetime.today().date()
    else:
        end = pd.to_datetime(end_date).date()

    # compute the first date so that there are exactly 'num_days' days total
    start = end - timedelta(days=num_days -1)

    # build a date index
    dates = pd.date_range(start=start, end=end, freq='D')

    # generate random floats in [1, 100], rounded to 2 decimals
    values = np.round(np.random.uniform(1.0, 100.0, size=num_days), 2)

    data = {
        'sale_date': dates,
        'sales': values
    }

    dataframe = pd.DataFrame(data)
    return dataframe