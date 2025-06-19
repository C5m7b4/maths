
from playgrounds.atrax.hold.atrax_column import AtraxColumn


class Atrax:
    """A simple data manipulation library for handling tabular data."""
    def __init__(self, data: list[dict]):
        """
        Initialize Atrax with a list of dictionaries representing rows of data.

            Parameters:
            data (list[dict]): A list of dictionaries where each dictionary represents a row of data
        """
        self.data = data
        self.columns = list(data[0].keys()) if data else []

    def head(self, n=5):
        """Return the first n rows of the data."""
        return Atrax(self.data[:n])
    
    def shape(self):
        """Return the shape of the data as a tuple (rows, columns)."""
        return (len(self.data), len(self.columns))

    def __getitem__(self, key):
        """Get a column or a list of columns from the data.
        If a string is passed, it returns the column as a list.
        If a list of strings is passed, it returns a list of lists for each column.
        """
        if isinstance(key, str):
            # return a list of values for a single column
            return AtraxColumn([row.get(key, None) for row in self.data], name=key)
        
        elif isinstance(key, list):
            # return a new Atrax with only selected columns
            if all(isinstance(k, str) for k in key):
                filtered_data = [
                    {col: row.get(col, None) for col in key} for row in self.data
                ]
                return Atrax(filtered_data)
            elif all(isinstance(k, bool) for k in key):
                # boolean mask filtering
                if len(key) != len(self.data):
                    raise ValueError("Boolean mask length must match number of rows.")
                filtered = [row for row, keep in zip(self.data, key) if keep]
                return Atrax(filtered)
            
        raise TypeError("Invalid key type.")

        
    def filter(self, func):
        return Atrax([row for row in self.data if func(row)])
    
    def describe(self):
        """Return a summary of the numeric columns in the data.
        This method calculates the mean, standard deviation, min, max, and count for each numeric column.
        
        NOTE: non-numeric columns are ignored in this summary."""

        from statistics import mean, stdev
        summary_data = []

        for col in self.columns:
            if not isinstance(self.data[0][col], (int, float)):
                continue

            col_data = [row[col] for row in self.data]
            summary_data.append({
                'column': col,
                'mean': mean(col_data),
                'std': stdev(col_data) if len(col_data) > 1 else 0.0,
                'min': min(col_data),
                'max': max(col_data),
                'count': len(col_data)
            })

        summary_rows = []
        for stat in ['mean', 'std', 'min', 'max', 'count']:
            row = {'stat': stat}
            for summary in summary_data:
                row[summary['column']] = summary[stat]
            summary_rows.append(row)

        return Atrax(summary_rows)
    
    def info(self):
        """Return a summary of the data including the number of rows, columns, and data types."""
        print(f"<class 'atrax.Atrax'>")
        print(f"Data columns (total {len(self.columns)}):")

        for col in self.columns:
            col_data = [row.get(col, None) for row in self.data]
            non_null = sum(x is not None for x in col_data)
            dtype = type(col_data[0]).__name__ if col_data else "Unknown"
            print(f"  {col:<15} Non-Null Count: {non_null:<5} Dtype: {dtype}")

        print(f"dtypes: {len(set(type(row[col]).__name__ for row in self.data for col in self.columns if col in row))}")
        print(f"Memory usage: {len(self.data) * len(self.columns) * 8} bytes (est.)")     

    def value_counts(self, column):  
        """Return the counts of unique values in a specified column."""
        from collections import Counter
        if column not in self.columns:
            raise ValueError(f"Column '{column}' does not exist in the data.")

        counts = Counter(row[column] for row in self.data)
        result = [{'value': k, 'count': v} for k, v in counts.items()]
        result.sort(key=lambda x: x['count'], reverse=True)
        return Atrax(result)   
    
    def column(self, key):
        """Return a single column as a new Atrax table."""
        if key not in self.columns:
            raise KeyError(f"Column '{key}' not found.")
        return Atrax([{key: row[key]} for row in self.data])

    def columns(self, keys):
        """Return multiple columns as a new Atrax table."""
        for key in keys:
            if key not in self.columns:
                raise KeyError(f"Column '{key}' not found.")
        return Atrax([{k: row[k] for k in keys} for row in self.data])













    def __repr__(self):
        """Return a string representation of the data."""
        display = [','.join(self.columns)]
        for row in self.data[:5]:
            display.append(','.join(str(row[col]) for col in self.columns))
        if len(self.data) > 5:
            display.append('...')
        return '\n'.join(display)
    
    def _repr_html_(self):
        """Return a HTML representation of the data.
        This method is used by Jupyter to display the data in a table format."""
        if not self.data:
            return "<p><b>Empty DataFrame</b></p>"
        
        html = "<table>"

        # header
        html += "<thead><tr>"
        for col in self.columns:
            html += f"<th>{col}</th>"
        html += "</tr></thead>"

        # body
        html += "<tbody>"
        for row in self.data[:10]:
            html += "<tr>"
            for col in self.columns:
                html += f"<td>{row.get(col, '')}</td>"
            html += "</tr>"
        html += "</tbody>"

        html += "</table>"
        return html     