def disabled(func):
    """Decorator that disables a function or method."""
    def wrapper(*args, **kwargs):
        raise NotImplementedError(f"The method '{func.__name__}' is currently disabled.")
    return wrapper
