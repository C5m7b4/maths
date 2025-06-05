


def custom_ln(x, terms=100):
    if x <= 0:
        raise ValueError("x must be > 0")

    y = (x - 1) / (x + 1)
    #print(f"y: {y}")
    result = 0
    for n in range(1, terms * 2, 2):
        result += (1 / n) * (y ** n)
    return 2 * result