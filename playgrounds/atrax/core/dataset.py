import statistics
import csv
import io
from .series import Series
from datetime import datetime

class DataSet:

    @property
    def index(self):
        return self._index

    @property
    def loc(self):
        return _LocIndexer(self)
    

    @property
    def iloc(self):
        return _iLocIndexer(self)
    
    def __init__(self, data: list[dict]):
        """Initialize the DataSet.
        
        Parameters:
        -----------
            data: (list[dict] or dict[list]): Either row oriented or column oriented data.
        """
        if isinstance(data, dict):
            lengths = [len(v) for v in data.values()]
            if len(set(lengths)) != 1:
                raise ValueError("All columns must have the same length")

            keys = list(data.keys())
            values = zip(*data.values())
            data = [dict(zip(keys, row)) for row in values]


        self.data = data
        self.columns = list(data[0].keys()) if data else []
        self._index_name = None
        self._index = list(range(len(data)))

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
        if not self.data:
            return "<i>Empty DataSet</i>"

        headers = self.columns.copy()
        show_index = self._index_name is not None

        # Create header row
        header_html = "<th></th>" if show_index else ""
        header_html += "".join(f"<th>{col}</th>" for col in headers)

        # Create data rows
        body_html = ""
        for idx, row in zip(self._index, self.data):
            row_html = ""
            if show_index:
                if isinstance(idx, datetime):
                    idx_str = idx.strftime('%Y-%m-%d')
                else:
                    idx_str = str(idx)
                row_html += f"<td><strong>{idx_str}<strong></td>"
            row_html += "".join(f"<td>{row.get(col, '')}</td>" for col in headers)
            body_html += f"<tr>{row_html}</tr>"

        return f"""
        <table>
            <thead><tr>{header_html}</tr></thead>
            <tbody>{body_html}</tbody>
        </table>
        """

    
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
        print(f"columns (total {len(self.columns)}):")
        if not self.data:
            print("   No data available")
            return

        if self._index_name and self._index:
            index_sample = self._index[0]
            if isinstance(index_sample, datetime):
                dtype = "datetime"
            elif isinstance(index_sample, int):
                dtype = "int"
            elif isinstance(index_sample, float):
                dtype = "float"
            elif isinstance(index_sample, str):
                dtype = "str"
            else:
                dtype = type(index_sample).__name__

            print(f"Index: {len(self._index)} entries")
            print(f"  name: {self._index_name}")
            print(f"  dtype: {dtype}")
            print("")

        # Now print column info
        col_stats = {}

        for col in self.columns:
            values = [row.get(col) for row in self.data]
            non_nulls = [v for v in values if v is not None]

            sample = non_nulls[0] if non_nulls else None
            dtype = "unknown"

            if sample is None:
                dtype = "NoneType"
            elif isinstance(sample, int):
                dtype = "int"
            elif isinstance(sample, float):
                dtype = "float"
            elif isinstance(sample, datetime):
                dtype = "datetime"
            elif isinstance(sample, bool):
                dtype = "bool"
            elif isinstance(sample, str):
                dtype = "str"

            col_stats[col] = {
                "dtype": dtype,
                "non_null": len(non_nulls),
                "total": len(values),
            }

        print(f"{'Column':<15} | {'Type':<10} | {'Non-Null':<10} | {'Total':<10}")
        print("-" * 50)
        for col, stats in col_stats.items():
            print(f"{col:<15} | {stats['dtype']:<10} | {stats['non_null']:<10} | {stats['total']}")  

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
        
    def reset_index(self, inplace=False):
        """Reset the index of the DataSet.
        
        Parameters:
        -----------
            inplace: (bool): If True, modify the current DataSet; if False, return a new DataSet.
        Returns:
        -----------
            DataSet: A new DataSet object with reset index.
        """
        if inplace:
            self.data = list(self.data)  # rebind reference
            return None
        else:
            return DataSet(list(self.data))
        
    def set_index(self, column, inplace=True, drop=False):
        """Set a column as the index of the DataSet.
        
        Parameters:
        -----------
            column: (str): The column name to set as index.
            inplace: (bool): If True, modify the current DataSet; if False, return a new DataSet.
            drop: (bool): if True, remove column from data
        Returns:
        -----------
            DataSet: A new DataSet object with the specified column as index.
        """
        if column not in self.columns:
            raise KeyError(f"Column '{column}' not found in dataset.")
        
        index_vals = [row[column] for row in self.data]
        
        if drop:
            new_data = [{k: v for k, v in row.items() if k != column} for row in self.data]
        else:
            new_data = self.data

        if inplace:
            self._index_name = column
            self._index = index_vals
            if drop:
                self.data = new_data
                self.columns = list(new_data[0].keys()) if new_data else []
            return None
        else:
            new_ds = DataSet(new_data)
            new_ds._index_name = column
            new_ds._index = index_vals
            return new_ds
        
    def to_dict(self):
        """Convert the DataSet to a list of dictionaries."""
        return list(self.data)
    
    def to_csv(self, path=None):
        """
        Convert the DataSet to CSV string or write to file.

        Parameters:
            path (str): If given, writes CSV to this file path

        Returns:
            str if path is None
        """
        import csv
        import io

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=self.columns)
        writer.writeheader()
        writer.writerows(self.data)

        if path:
            with open(path, 'w', newline='') as f:
                f.write(output.getvalue())
            return None
        else:
            return output.getvalue()  
        
    def to_pandas(self):
        """Convert the DataSet to a pandas DataFrame."""
        import pandas as pd

        df = pd.DataFrame(self.data)
        
        # set index if it exists
        if self._index_name and self._index:
            df.index = pd.Index(self._index, name=self._index_name)

        return df
        
    def convert_column(self, column: str, func):
        """Convert a column using a function.
        
        Parameters:
        -----------
            column: (str): The column name to convert.
            func: (callable): A function that takes a single value and returns the converted value.
        """
        if row in self.data:
            if column in row:
                try:
                    row[column] = func(row[column])
                except:
                    pass
    def astype(self, dtype_map: dict):
        """Convert columns to specified data types.
        
        Parameters:
        -----------
            dtype_map: (dict): A dictionary mapping column names to target data types.
        Returns:
        -----------
            DataSEt: A new DataSet with converted columns
        """
        new_data = []

        for row in self.data:
            new_row = row.copy()
            for col, dtype in dtype_map.items():
                if col in new_row:
                    try:
                        new_row[col] = dtype(new_row[col])

                    except:
                        new_row[col] = None # or raise error
            new_data.append(new_row)
        new_ds = DataSet(new_data)

        # preserve the index
        new_ds._index = self._index
        new_ds._index_name = self._index_name
        return new_ds

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
        # ✅ CASE 1: Tuple → (row_filter, col_filter)
        if isinstance(key, tuple):
            row_filter, col_filter = key

        # ✅ CASE 2: Single filter → callable or boolean list
        elif callable(key) or (isinstance(key, list) and all(isinstance(b, bool) for b in key)):
            row_filter = key
            col_filter = self.dataset.columns  # return all columns

        # ✅ CASE 3: Single label (e.g., "2025-03-02")
        else:
            key_val = key
            if self.dataset._index:
                index_sample = self.dataset._index[0]
                if isinstance(index_sample, datetime) and isinstance(key, str):
                    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d"):
                        try:
                            key_val = datetime.strptime(key, fmt)
                            break
                        except ValueError:
                            continue
            matched_rows = [
                row for idx, row in zip(self.dataset._index, self.dataset.data)
                if idx == key_val
            ]
            return DataSet(matched_rows)

        # ✅ Apply row filtering
        if isinstance(row_filter, list) and all(isinstance(b, bool) for b in row_filter):
            filtered = [row for row, keep in zip(self.dataset.data, row_filter) if keep]
        elif callable(row_filter):
            filtered = [row for row in self.dataset.data if row_filter(row)]
        else:
            filtered = self.dataset.data  # fallback (no filter)

        # ✅ Apply column projection
        if isinstance(col_filter, str):
            col_filter = [col_filter]

        result_data = [{col: row.get(col) for col in col_filter} for row in filtered]
        return DataSet(result_data)





class _iLocIndexer:
    def __init__(self, dataset):
        self.dataset = dataset

    def __getitem__(self, key):
        row_idx, col_idx = key

        rows = self.dataset.data[row_idx] if isinstance(row_idx, slice) else [self.dataset.data[row_idx]]

        col_names = self.dataset.columns[col_idx] if isinstance(col_idx, slice) else [self.dataset.columns[i] for i in col_idx]

        filtered = [{k: row[k] for k in col_names if k in row} for row in rows]
        return DataSet(filtered)
