

def SSE(y_true, y_pred):
    """
    Calculate the sum of squared errors (SSE) between true and predicted values.

    Args:
        y_true (list or np.array): True values.
        y_pred (list or np.array): Predicted values.

    Returns:
        float: The sum of squared errors.
    """
    return sum((y - y_hat) ** 2 for y, y_hat in zip(y_true, y_pred))

def MSE(y_true, y_pred):
    """
    Calculate the mean squared error (MSE) between true and predicted values.

    Args:
        y_true (list or np.array): True values.
        y_pred (list or np.array): Predicted values.

    Returns:
        float: The mean squared error.
    """
    n = len(y_true)
    return SSE(y_true, y_pred) / n if n > 0 else float('inf')


def RMSE(y_true, y_pred):
    """
    Calculate the root mean squared error (RMSE) between true and predicted values.

    Args:
        y_true (list or np.array): True values.
        y_pred (list or np.array): Predicted values.

    Returns:
        float: The root mean squared error.
    """
    mse = MSE(y_true, y_pred)
    return mse ** 0.5 if mse >= 0 else float('inf')

def MAE(y_true, y_pred):
    """
    Calculate the mean absolute error (MAE) between true and predicted values.

    Args:
        y_true (list or np.array): True values.
        y_pred (list or np.array): Predicted values.

    Returns:
        float: The mean absolute error.
    """
    n = len(y_true)
    return sum(abs(y - y_hat) for y, y_hat in zip(y_true, y_pred)) / n if n > 0 else float('inf')

def MAPE(y_true, y_pred):
    """
    Calculate the mean absolute percentage error (MAPE) between true and predicted values.

    Args:
        y_true (list or np.array): True values.
        y_pred (list or np.array): Predicted values.

    Returns:
        float: The mean absolute percentage error.
    """
    n = len(y_true)
    return sum(abs((y - y_hat) / y) for y, y_hat in zip(y_true, y_pred) if y != 0) / n if n > 0 else float('inf')

def SMAPE(y_true, y_pred):
    """
    Calculate the symmetric mean absolute percentage error (SMAPE) between true and predicted values.

    Args:
        y_true (list or np.array): True values.
        y_pred (list or np.array): Predicted values.

    Returns:
        float: The symmetric mean absolute percentage error.
    """
    n = len(y_true)
    return sum(abs(y - y_hat) / ((abs(y) + abs(y_hat)) / 2) for y, y_hat in zip(y_true, y_pred) if (abs(y) + abs(y_hat)) != 0) / n if n > 0 else float('inf')