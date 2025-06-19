from .series import Series

class DataSet:
    def __init__(self, data: list[dict]):
        self.data = data
        self.columns = list(data[0].keys()) if data else []

    def __getitem__(self, key):
        if isinstance(key, str):
            # return a Series
            return Series([row[key] for row in self.data], name=key)
        elif isinstance(key, list):
            if all(isinstance(k, str) for k in key):
                # subset of columns
                return DataSet([{k: row[k] for k in key} for row in self.data])
            elif all(isinstance(k, bool) for k in key):
                if len(key) != len(self.data):
                    raise ValueError("Boolean index must match the length of the data.")
                return DataSet([row for row, keep in zip(self.data, key) if keep])
        raise TypeError("Unsuppored key type")

    def __repr__(self):
        preview = self.data[:10]
        lines = [",".join(self.columns)]
        for row in preview:
            lines.append(",".join(str(row[col]) for col in self.columns))
        if len(self.data) > 10:
            lines.append("...")
        return "\n".join(lines)
    
    def _repr_html_(self):
        if not self.data:
            return "<p><b>Empty Dataset</b></p>"
        html = "<table><thead><tr>"
        html += "".join(f"<th>{col}</th>" for col in self.columns)
        html += "</tr></thead><tbody>"

        for row in self.data[:10]:
            html += "<tr>" + "".join(f"<td>{row[col]}</td>" for col in self.columns) + "</tr>"
        if len(self.data) > 10:
            html += f"<tr><td colspan='{len(self.columns)}'>... {len(self.data) - 10} more rows</td></tr>"
        html += "</tbody></table>"
        return html
