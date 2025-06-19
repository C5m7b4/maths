import io
import csv
from datetime import datetime
import pandas as pd


from .core.series import Series
from .core.dataset import DataSet

class Atrax:
    Series = Series
    DataSet = DataSet

    @staticmethod
    def read_pandas(df: pd.DataFrame) -> 'DataSet':
        """Convert a pandas DataFrame to a DataSet.
        
        Parameters:
        -----------
            df: (pd.DataFrame): The DataFrame to convert.
            
        Returns:
        -----------
            DataSet: A DataSet object containing the data from the DataFrame.
        """
        records = df.to_dict(orient='records')
        ds = DataSet(records)

        # set index if its named
        if df.index.name:
            ds._index_name = df.index.name
            ds._index = df.index.tolist()

        return ds


    @staticmethod
    def read_csv(path_or_str, from_string=False, encoding='utf-8', converters=None, usecols=None, parse_dates=None):
        """Read a CSV file or string into a dataset.
        
        Parameters:
        -----------
            path_or_str: (str): Path to the CSV file or a CSV formatted string.
            from_string: (bool): If True, treats path_or_str as a string, otherwise as a file path.
            encoding: (str): Encoding to use when reading the file
            converters: (dict): Optional dict of colum: function
            usecols: (list): Optionaal list of columns to keep
            
        Returns:
        -----------
            DataSet: A DataSet object containing the data from the CSV.
        """
        if from_string:
            f = io.StringIO(path_or_str)
        else:
            f = open(path_or_str, newline='')

        reader = csv.DictReader(f)
        rows = []

        # attempt numeric conversion
        for row in reader:
            parsed_row = {}
            for k, v in row.items():
                if usecols and k not in usecols:
                    continue

                # Handle custom converter
                if converters and k in converters:
                    try:
                        parsed_row[k] = converters[k](v)
                        continue
                    except Exception:
                        parsed_row[k] = v
                        continue

                # Handle datetime parsing
                if parse_dates and k in parse_dates:
                    try:
                        parsed_row[k] = datetime.fromisoformat(v)
                        continue
                    except ValueError:
                        try:
                            parsed_row[k] = datetime.strptime(v, "%Y-%m-%d")
                        except:
                            parsed_row[k] = v
                        continue

                # Try numeric fallback
                try:
                    parsed_row[k] = float(v) if '.' in v else int(v)
                except:
                    parsed_row[k] = v

            rows.append(parsed_row)
                
        return DataSet(rows)
    
    @staticmethod
    def read_sql(query, conn):
        cur = conn.cursor()
        cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        return DataSet([dict(zip(columns, row)) for row in rows])    