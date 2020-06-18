def set_module(module):
    """
    Decorator for overriding __module__ on a function or class

    Example usage::
        @set_module('balltic')
        def example():
            pass
        assert example.__module__ == 'balltic'
    """
    def decorator(func):
        if module is not None:
            func.__module__ = module
        return func
    return decorator
