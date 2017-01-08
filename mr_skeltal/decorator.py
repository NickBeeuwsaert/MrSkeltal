import functools


class reify(object):
    def __init__(self, method):
        self.method = method
        functools.update_wrapper(self, method)

    def __get__(self, instance, owner=None):
        value = self.method(instance)
        setattr(instance, self.method.__name__, value)
        return value
