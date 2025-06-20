from datetime import datetime

class Series:

    @property
    def iloc(self):
        return _Iloc(self)

    @property
    def loc(self):
        return _Loc(self)
    


    def __init__(self, data, name=None, index=None):
        """
        One-dimensional labeled array for Atrax.

        Parameters
        ----------
        data : list
            A list of values.
        name : str, optional
            The name of the series.
            defaults to None, which means no name is assigned.

        Examples
        --------
        >>> from atrax import Atrax
        >>> s = Atrax.Series([1, 2, 3, 4], name="numbers")
        >>> print(s)
        0: 1
        1: 2
        2: 3
        3: 4
        """
        self.data = data
        self.name = name or ""
        self.index = index or list(range(len(data)))
        if len(self.data) != len(self.index):
            raise ValueError("Length of index must match length of data.")
        self.dtype = self._infer_dtype()

    def _infer_dtype(self):
        if all(isinstance(x, int) for x in self.data):
            return "int"
        elif all(isinstance(x, (int, float)) for x in self.data):
            return "float"
        else:
            return "object"

    def __repr__(self):
        lines = [f"{idx}   {val}" for idx, val in zip(self.index[:10], self.data[:10])]
        if len(self.data) > 10:
            lines.append(f"...({len(self.data)} total)")
        lines.append(f"Name: {self.name}, dtype: {self.dtype}")
        return "\n".join(lines)
    
    def __len__(self):
        """Get the number of elements in the Series."""
        return len(self.data)
    
    def __getitem__(self, i):
        """Get an item from the Series by index."""
        return self.data[i]
    
    def __gt__(self, other):
        result =  [x > other for x in self.data]
        return Series(result, name=f"({self.name} > {other})")
    
    
    def __lt__(self, other): 
        result =  [x < other for x in self.data]
        return Series(result, name=f"({self.name} < {other})")
    
    def __ge__(self, other):        
        result =  [x >= other for x in self.data]
        return Series(result, name=f"({self.name} >= {other})")
    
    def __le__(self, other):        
        result = [x <= other for x in self.data]
        return Series(result, name=f"({self.name} <= {other})")
    
    def __eq__(self, other):        
        result = [x == other for x in self.data]
        return Series(result, name=f"({self.name} == {other})")
    
    def __ne__(self, other):        
        result = [x != other for x in self.data]
        return Series(result, name=f"({self.name} != {other})")
    
    def _binary_op(self, other, op):
        if isinstance(other, Series):
            if len(other.data) != len(self.data):
                raise ValueError("Cannot perform operation: Series must have the same length.")
            return Series([op(a,b) for a,b in zip(self.data, other.data)], name=self.name)
        else:
            return Series([op(a, other) for a in self.data], name=self.name)

    def __add__(self, other): return self._binary_op(other, lambda a, b: a + b)
    def __sub__(self, other): return self._binary_op(other, lambda a, b: a - b)
    def __mul__(self, other): return self._binary_op(other, lambda a, b: a * b)
    def __truediv__(self, other): return self._binary_op(other, lambda a, b: a / b)
    def __floordiv__(self, other): return self._binary_op(other, lambda a, b: a // b)
    def __mod__(self, other): return self._binary_op(other, lambda a, b: a % b)
    def __pow__(self, other): return self._binary_op(other, lambda a, b: a ** b)

    def __and__(self, other):
        if not isinstance(other, Series):
            raise TypeError("Operand must be a Series.")
        if len(other.data) != len(self.data):
            raise ValueError("Cannot perform operation: Series must have the same length.")
        return Series([a and b for a,b in zip(self.data, other.data)], name=f"({self.name}) & {other.name}")
    
    def __or__(self, other):
        if not isinstance(other, Series):
            raise TypeError("Operand must be a Series.")
        if len(other.data) != len(self.data):
            raise ValueError("Cannot perform operation: Series must have the same length.")
        return Series([a or b for a, b in zip(self.data, other.data)], name=f"({self.name}) | {other.name}")

    def __invert__(self):
        return Series([not x for x in self.data], name=f"(~{self.name})")

    def head(self, n=5):
        """
        Return the first n elements of the Series.
        Parameters:
        n (int): The number of elements to return. Defaults to 5.
        Returns:
        Series: A new Series containing the first n elements.
        """
        return Series(self.data[:n], name=self.name, index=self.index[:n])
    
    def tail(self, n=5):
        """
        Return the last n elements of the Series.
        Parameters:
        n (int): The number of elements to return. Defaults to 5.
        Returns:
        Series: A new Series containing the last n elements.
        """
        return Series(self.data[-n:], name=self.name, index=self.index[-n:])
    
    def unique(self):
        """
        Return the unique values in the Series.
        Returns:
        Series: A new Series containing the unique values.
        """
        unique_data = list(set(self.data))
        return Series(unique_data, name=f"Unique({self.name})", index=list(range(len(unique_data))))
    
    def nunique(self):
        """
        Return the number of unique values in the Series.
        Returns:
        int: The number of unique values.
        """
        return len(set(self.data))
    
    def isin(self, values):
        """
        Check if each element in the Series is in the provided list of values.
        Parameters:
        values (list): A list of values to check against.
        Returns:
        Series: A new Series containing boolean values indicating membership.
        """
        return Series([x in values for x in self.data], name=f"IsIn({self.name})", index=self.index)
    
    def between(self, left, right, inclusive=True):
        """
        Check if each element in the Series is between two values.
        Parameters:
        left (int/float): The lower bound.
        right (int/float): The upper bound.
        inclusive (bool): Whether to include the bounds. Defaults to True.
        Returns:
        Series: A new Series containing boolean values indicating if each element is between the bounds.
        """
        if inclusive:
            return Series([left <= x <= right for x in self.data], name=f"Between({self.name}, {left}, {right})")
        else:
            return Series([left < x < right for x in self.data], name=f"Between({self.name}, {left}, {right}, exclusive)")

    def to_list(self):
        """
        Convert the Series to a list.
        Returns:
        list: The data in the Series as a list.
        """
        return self.data
    
    def apply(self, func):
        return Series([func(x) for x in self.data], name=self.name)
    
    def astype(self, dtype):
        cast_fn = {
            'int': int,
            'float': float,
            'str': str,
            'object': lambda x: x # no-op
        }.get(dtype)

        if cast_fn is None:
            raise ValueError(f"Unsupported dtype: {dtype}")
        
        new_data = [cast_fn(x) for x in self.data]
        return Series(new_data, name=self.name)
    
    def _repr_html_(self):
        """
        Return a string representation of the Series in HTML format.
        Returns:
        str: HTML representation of the Series.
        """
        html = "<table style='border-collapse: collapse;'>"
        for idx, val in zip(self.index[:10], self.data[:10]):
            html += f"<tr><td style=''>{idx}</td>"
            html += f"<td style=''>{val}</td></tr>"
        html += f"<tr><td colspan='2' style='font-style: bold; font-size:1.1rem;'>Name: {self.name}, dtype: {self.dtype}</td></tr>"
        if len(self.data) > 10:
            html += f"<tr><td colspan='2'><i>...{len(self.data) - 10} more</i></td></tr>"
        html += "</table>"
        return html 
    
    def to_datetime(self, format='%Y-%m-%d', errors='raise'):
        """
        Convert the Series to datetime objects.
        
        Parameters:
        format (str): The format of the date strings. Defaults to '%m/%d/%Y'.
        errors (str): 'raise' to throw errors, 'coerce' to return None on failure
        
        Returns:
        Series: A new Series with datetime objects.
        """
        converted = []

        for val in self.data:
            if isinstance(val, datetime):
                converted.append(val)
            elif isinstance(val, str):
                try:
                    converted.append(datetime.strptime(val, format))
                except Exception as e:
                    if errors == 'coerce':
                        converted.append(None)
                    else:
                        raise ValueError(f"Failed to parse '{val}' as datetime: {e}")
            else:
                if errors == 'coerce':
                    converted.append(None)
                else:
                    raise ValueError(f"Unsupported type for to_datetime: {type(val)}")
        return Series(converted, name=self.name, index=self.index)
    
    def astype(self, dtype):
        """
        Convert the Series to a specified data type.
        
        Parameters:
        dtype (str): dtype (type): The Python type to cast to (e.g., int, float, str)
        
        Returns:
        Series: A new Series with the converted data type.
        """
        new_data = []
        for val in self.data:
            try:
                new_data.append(dtype(val))
            except:
                new_data.append(None)
        return Series(new_data, name=self.name, index=self.index)
    
    


class _Iloc:
    def __init__(self, series):
        self.series = series

    def __getitem__(self, i):
        if isinstance(i, slice):
            return Series(self.series.data[i], name=self.series.name, index=self.series.index[i])
        return self.series.data[i]
    


class _Loc:
    def __init__(self, series):
        self.series = series

    def __getitem__(self, key):
        if isinstance(key, list):
            index_map = {k:v for k, v in zip(self.series.index, self.series.data)}
            return Series([index_map[k] for k in key], name=self.series.name, index=key)
        elif isinstance(key, slice):
            raise NotImplementedError("Slicing by label is not implemented yet.")
        else:
            # single label lookup
            idx = self.series.index.index(key)
            return self.series.data[idx] 