import io
import csv
from datetime import datetime
import pandas as pd


from .core.series import Series
from .core.dataset import DataSet
from .core.qcut import qcut

class Atrax:
    Series = Series
    DataSet = DataSet
    qcut = qcut

    @staticmethod
    def date_range(start, end=None, periods=None, freq='D'):
        """Generate a list of datetime values.
        
        Parameters:
            start (str | datetime): start date
            end (str | datetime): end date (optional if periods is given)
            periods (int): number of periods to generate
            freq (str): frequency string (e.g. 'D', 'W' 'M')

        Returns:
            list[datetime]: list of datetime objects
        """
        if isinstance(start, str):
            start = pd.to_datetime(start)
        if isinstance(end, str) and end is not None:
            end = pd.to_datetime(end)

        dr = pd.date_range(start=start, end=end, periods=periods, freq=freq)
        #return list[dr.to_pydatetime()]
        return dr


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
    def read_sql(query: str, conn, index_col=None) -> "DataSet":
        """
        Read SQL query into an Atrax DataSet.

        Parameters:
            query (str): SQL query to execute
            conn: Database connection (sqlite3 or psycopg2 or SQLAlchemy)
            index_col (str): Optional column to use as index

        Returns:
            DataSet
        """
        import pandas as pd

        try:
            # Use pandas for broad compatibility
            df = pd.read_sql_query(query, conn)

            # If index_col is provided, move it to index
            if index_col and index_col in df.columns:
                df.set_index(index_col, inplace=True)

            return Atrax.read_pandas(df)

        except Exception as e:
            raise RuntimeError(f"Failed to execute query: {e}")
    