from functools import wraps


def auto_logger(logger):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Called {func.__name__} with args={args}, kwargs={kwargs}")
            result = func(*args, **kwargs)
            logger.info(f"{func.__name__} returned {result}")
            return result

        return wrapper

    return decorator
