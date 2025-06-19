# core.py (inside atrax/)
class Series:
    def __init__(self, data, name=None):
        self.data = data
        self.name = name or ""

class DataSet:
    def __init__(self, data):
        self.data = data