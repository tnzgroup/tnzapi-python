import functools
import warnings


def accept_legacy_kwargs(mapping: dict):
    """Decorator that translates deprecated snake_case keyword arguments into
    their PascalCase equivalents before calling the wrapped method, so
    existing integrations built against the old kwarg names keep working
    (deprecated, not removed) per this library's PATCH/MINOR compatibility
    commitment. mapping is {old_snake_case_name: new_PascalCase_name}.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for old_name, new_name in mapping.items():
                if old_name in kwargs:
                    if new_name in kwargs:
                        raise TypeError(
                            f"{func.__name__}() got both '{new_name}' and its deprecated alias "
                            f"'{old_name}' - pass only one"
                        )
                    warnings.warn(
                        f"{func.__name__}({old_name}=...) is deprecated, use {new_name}=... instead",
                        DeprecationWarning,
                        stacklevel=2,
                    )
                    kwargs[new_name] = kwargs.pop(old_name)
            return func(*args, **kwargs)
        return wrapper
    return decorator
