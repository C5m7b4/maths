def custom_covariance(ds, x, y):
    return ((ds[x] - ds[x].mean()) * (ds[y] - ds[y].mean())).sum()/ (len(ds) - 1)