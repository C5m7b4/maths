import statistics
from .series import Series

class DataSet:

    @property
    def loc(self):
        return _LocIndexer(self)
    

    @property
    def iloc(self):
        return _iLocIndexer(self)
    


    def __init__(self, data: list[dict]):
        self.data = data
        self.columns = list(data[0].keys()) if data else []

    def __getitem__(self, key):
        if isinstance(key, str):
            # return a Series
            return Series([row.get(key) for row in self.data], name=key)
        
        elif isinstance(key, Series) and all(isinstance(val, bool) for val in key.data):
            # filter rows using a bookean series
            if len(key.data) != len(self.data):
                raise ValueError("Boolean Series must match the length of the dataset.")
            filtered = [row for row, flag in zip(self.data, key.data) if flag]
            return DataSet(filtered)
        
        elif isinstance(key, list):
            # column subset
            return DataSet([{k: row[k] for k in key if k in row} for row in self.data])
        
        else:
            raise TypeError("Key must be a string (column), list of strings (subset), or Series(boolean mask)")

    def __setitem__(self, key, value):
        if isinstance(value, Series):
            if len(value.data) != len(self.data):
                raise ValueError("Series length must match Dataset length.")
            for row, val in zip(self.data, value.data):
                row[key] = val
            if key not in self.columns:
                self.columns.append(key)
        else:
            raise TypeError("Only Series assignment is supported at the moment.")

    def __repr__(self):
        lines = [", ".join(self.columns)]
        for row in self.data[:10]:
            lines.append(", ".join(str(row.get(col, "")) for col in self.columns))
        if len(self.data) > 10:
            lines.append(f"... ({len(self.data)} rows total)")
        return "\n".join(lines)
    
    def _repr_html_(self):
        html = "<table style='border-collapse: collapse;'>"
        html += "<thead><tr>" + "".join(f"<th>{col}</th>" for col in self.columns) + "</tr></thead><tbody>"
        for row in self.data[:10]:
            html += "<tr>" + "".join(f"<td>{row.get(col, '')}</td>" for col in self.columns) + "</tr>"
        if len(self.data) > 10:
            html += f"<tr><td colspan='{len(self.columns)}'><i>... {len(self.data) - 10} more rows</i></td></tr>"
        html += "</tbody></table>"
        return html
    
    def head(self, n=5):
        """Return the first n rows of the dataset."""
        return DataSet(self.data[:n])

    def tail(self, n=5):
        """Return the last n rows of the dataset."""
        return DataSet(self.data[-n:])
    
    def shape(self):
        """Return the shape of the dataset as a tuple (rows, columns)."""
        return (len(self.data), len(self.columns))

    def columns(self):
        """Return the list of column names in the dataset."""
        return self.columns

    def describe(self):
        """Return a summary of the numeric columns in the dataset.
        This method calculates the mean, standard deviation, min, max, and count for each numeric column.
        Non-numeric columns are ignored in this summary.
        """
        numeric_cols = {
            col: [row[col] for row in self.data if isinstance(row.get(col), (int, float))] for col in self.columns
        }
        summary_rows = []

        def percentile(data, q):
            data= sorted(data)
            idx = int(round(q * (len(data) - 1)))
            return data[idx]
        
        for stat in ['mean', 'std', 'min', 'Q1', 'median', 'Q3', 'max', 'count']:
            row = {'stat': stat}
            for col, values in numeric_cols.items():
                if not values:
                    row[col] = None
                    continue

                if stat == 'mean':
                    row[col] = round(statistics.mean(values), 2)
                elif stat == 'std':
                    row[col] = round(statistics.stdev(values), 2) if len(values) > 1 else 0.0
                elif stat == 'min':
                    row[col] = min(values)
                elif stat == 'Q1':
                    row[col] = percentile(values, 0.25)
                elif stat == 'median':
                    row[col] = statistics.median(values)
                elif stat == 'Q3':
                    row[col] = percentile(values, 0.75)
                elif stat == 'max':
                    row[col] = max(values)
                elif stat == 'count':
                    row[col] = len(values)
            summary_rows.append(row)

        return DataSet(summary_rows)
    
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

    def apply(self, func, axis=1):
        """Apply a function to each row (axis=1) or each column (axis=0).
        Currently supports only row-wise operations.
        
        Parameters:
        ------------
            func: callable
                A function that takes a row (dict) and returns a value or dict.
            axis: int, default 1
                Only axis=1 (row-wise) is currently supported
                
        Returns:
        -----------
        list or DataSet
        """
        if axis != 1:
            raise NotImplementedError("Only row-wise operations (axis=1) are currently supported.")
        
        results = [func(row) for row in self.data]

        # if function returns dicts, convert back to DtaSet
        if all(isinstance(r, dict) for r in results):
            return DataSet(results)
        else:
            return results
    
    def copy(self):
        """Return a deep copy of the DataSet."""
        return DataSet([row.copy() for row in self.data])
        
    def groupby(self, by):
        return GroupBy(self.data, by)
    
    def sort(self, by, ascending=True):
        if by not in self.columns:
            raise KeyError(f"Column '{by}' not found in dataset.")
        
        sorted_data = sorted(self.data, key=lambda row: row.get(by), reverse=not ascending)
        return DataSet(sorted_data)

    def filter(self, items=None, like=None):
        if items is not None:
            return DataSet([{k: row[k] for k in items if k in row} for row in self.data])
        
        elif like is not None:
            matching = [col for col in self.columns if like in col]
            return DataSet([{k: row[k] for k in matching if k in row} for row in self.data])
        
        else:
            raise ValueError("Must provide 'items' or 'like")
        
    def drop(self, columns=None, index=None, inplace=False):
        """Drop columns or rows frm dataset.
        
        Parameters:
        -----------
            columns: (list of str): List of column names to drop from the dataset.
            index :(list): list of row indexes to drop
            inplace: (bool): Modify the current DataSet or return a new one
        Returns:
        -----------
            DataSet: A new DataSet object with the specified columns removed.
        """
        new_data = self.data

        if index is not None:
            new_data = [row for i, row in enumerate(new_data) if i not in index]

        if columns:
            new_data = [{k: v for k, v in row.items() if k not in columns} for row in new_data]

        if inplace:
            self.data = new_data
            self.columns = list(new_data[0].keys()) if new_data else []
            return None
        else:
            return DataSet(new_data)



    def rename(self, columns=None, inplace=False):
        """Rename columns in the dataset.
        
        Parameters:
        -----------
            columns: (dict): A dictionary mapping old column names to new names.
            inplace: (bool): If True, modify the current DataSet; if False, return a new DataSet.
        Returns:
        -----------
            DataSet: A new DataSet object with renamed columns.
        """
        if not columns:
            return self
        
        new_data = []
        for row in self.data:
            new_row = {}
            for k, v in row.items():
                new_key = columns.get(k, k)
                new_row[new_key] = v
            new_data.append(new_row)
        
        if inplace:
            self.data = new_data
            self.columns = list(new_data[0].keys()) if new_data else []
            return None
        else:
            return DataSet(new_data)
        

class GroupBy:
    def __init__(self, data, by):
        self.by = by if isinstance(by, list) else [by]
        self.data = data
        self.groups = self._group_data()

    def _group_data(self):
        from collections import defaultdict
        grouped = defaultdict(list)
        for row in self.data:
            key = tuple(row[k] for k in self.by)
            grouped[key].append(row)
        return grouped
    
    def agg(self, agg_dict):
        result = []

        for group_key, rows in self.groups.items():
            # collect all values per column across the group
            col_data = {}
            for row in rows:
                for col, val in row.items():
                    col_data.setdefault(col, []).append(val)

            aggregated_row = {}
            for col, agg_funcs in agg_dict.items():
                values = col_data.get(col, [])

                if not isinstance(agg_funcs, list):
                    agg_funcs = [agg_funcs]

                for agg_func in agg_funcs:
                    if isinstance(agg_func, str):
                        colname = f"{col}_{agg_func}"
                        if agg_func == "sum":
                            aggregated_row[colname] = sum(values)
                        elif agg_func == "count":
                            aggregated_row[colname] = len(values)
                        elif agg_func == "max":
                            aggregated_row[colname] = max(values)
                        elif agg_func == "min":
                            aggregated_row[colname] = min(values)
                        elif agg_func == "mean":
                            aggregated_row[colname] = sum(values) / len(values)
                        else:
                            raise ValueError(f"Unsupported agg: {agg_func}")

                    elif callable(agg_func):
                        colname = f"{col}_{agg_func.__name__}"
                        aggregated_row[colname] = agg_func(values)

                    else:
                        raise TypeError("Aggregation must be string or function")

            # add group key back in
            for i, col in enumerate(self.by):
                aggregated_row[col] = group_key[i]
            result.append(aggregated_row)

        return DataSet(result)

    def sum(self):
        result = []
        for group_key, rows in self.groups.items():
            summary = {col: 0 for col in rows[0] if isinstance(rows[0][col], (int, float))}
            for row in rows:
                for col in summary:
                    summary[col] += row.get(col, 0)
            # add group key back
            for i, col in enumerate(self.by):
                summary[col] = group_key[i]
            result.append(summary)
        return DataSet(result)

    def mean(self):
        result = []
        for group_key, rows in self.groups.items():
            count = len(rows)
            summary = {col: 0 for col in rows[0] if isinstance(rows[0][col], (int, float))}
            for row in rows:
                for col in summary:
                    summary[col] += row.get(col, 0)
            for col in summary:
                summary[col] /= count
            for i, col in enumerate(self.by):
                summary[col] = group_key[i]
            result.append(summary)
        return DataSet(result)        


class _LocIndexer:
    def __init__(self, dataset):
        self.dataset = dataset

    def __getitem__(self, key):
        row_filter, col_filter = key

        # Handle row filter
        if isinstance(row_filter, Series):
            if len(row_filter.data) != len(self.dataset.data):
                raise ValueError("Row filter must match DataSet length")
            rows = [row for row, keep in zip(self.dataset.data, row_filter.data) if keep]
        else:
            raise TypeError("Row filter must be a Series")

        # Handle column filter
        if isinstance(col_filter, list):
            filtered = [
                {k: row[k] for k in col_filter if k in row}
                for row in rows
            ]
            return DataSet(filtered)
        else:
            raise TypeError("Column selector must be list of strings")


class _iLocIndexer:
    def __init__(self, dataset):
        self.dataset = dataset

    def __getitem__(self, key):
        row_idx, col_idx = key

        rows = self.dataset.data[row_idx] if isinstance(row_idx, slice) else [self.dataset.data[row_idx]]

        col_names = self.dataset.columns[col_idx] if isinstance(col_idx, slice) else [self.dataset.columns[i] for i in col_idx]

        filtered = [{k: row[k] for k in col_names if k in row} for row in rows]
        return DataSet(filtered)
