class AtraxColumn:
    def __init__(self, data, name=None):
        """
        Initialize ColumnView with a list of data.
        Parameters:
        data (list): A list of values representing the column data.
        """
        self.data = data
        self.name = name if name else "Unnamed Column"

    def __gt__(self, other):
        """
        Compare each element in the column with another value.
        Parameters:
        other: The value to compare against.
        Returns:
        list: A list of boolean values indicating if each element is greater than the other value."""
        return [x > other for x in self.data]
    
    def __lt__(self, other):
        """
        Compare each element in the column with another value.
        Parameters:
        other: The value to compare against.
        Returns:
        list: A list of boolean values indicating if each element is less than the other value."""        
        return [x < other for x in self.data]
    
    def __ge__(self, other):
        """
        Compare each element in the column with another value.
        Parameters:
        other: The value to compare against.
        Returns:
        list: A list of boolean values indicating if each element is greater than or equal to the other value."""         
        return [x >= other for x in self.data]
    
    def __le__(self, other):
        """
        Compare each element in the column with another value.
        Parameters:
        other: The value to compare against.
        Returns:
        list: A list of boolean values indicating if each element is less than or equal to the other value."""         
        return [x <= other for x in self.data]
    
    def __eq__(self, other):
        """
        Compare each element in the column with another value.
        Parameters:
        other: The value to compare against.
        Returns:
        list: A list of boolean values indicating if each element is equal to the other value."""         
        return [x == other for x in self.data]
    
    def __ne__(self, other):
        """
        Compare each element in the column with another value.
        Parameters:
        other: The value to compare against.
        Returns:
        list: A list of boolean values indicating if each element is not equal to the other value."""         
        return [x != other for x in self.data]
    
    def __repr__(self):
        """Return a string representation of the ColumnView."""            
        preview = self.data[:10]
        out = "\n".join(f"{i}: {v}" for i, v in enumerate(preview))
        if len(self.data) > 10:
            out += f"\n...({len(self.data)} total)"
        return out