def custom_correlation(ds, x, y):
    return (((ds[x] - ds[x].mean()) * (ds[y] - ds[y].mean())).sum()/(len(ds) - 1)) / (ds[x].std() * ds[y].std())