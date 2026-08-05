import warnings


def deprecated_alias(mapping):
    """Builds a PEP 562 module-level __getattr__ that serves old class names
    as aliases for their renamed replacement, e.g.
    __getattr__ = deprecated_alias({"SMSResponseDTO": SMSResponse})
    in a dtos/*.py module.

    `mapping` is {old_name: new_class}. The returned callable, when the
    module attribute lookup falls through to it (i.e. the old name is no
    longer a real module-level name), emits a DeprecationWarning and returns
    new_class ITSELF - not a copy or subclass - so isinstance/equality/
    identity checks against the old name keep working exactly as before,
    and there is only one class to ever keep in sync, not two. This alias
    is permanent (no planned removal), matching this project's
    backward-compatibility commitment.
    """
    def __getattr__(name):
        if name in mapping:
            new_cls = mapping[name]
            warnings.warn(
                f"{name} is deprecated, use {new_cls.__name__} instead",
                DeprecationWarning,
                stacklevel=2,
            )
            return new_cls
        raise AttributeError(f"module has no attribute {name!r}")

    return __getattr__
