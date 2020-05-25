#!python3
registry = {}


# 解决多参数方法重载问题
class MultiMethod(object):

    def __init__(self, name):
        self.name = name
        self.typemap = {}

    def __call__(self, *args, **kwargs):
        types = tuple(arg.__class__ for arg in args)
        func = self.typemap.get(types)
        if func is None:
            raise TypeError('no match')
        return func(*args)

    def register(self, types, func):
        if types in self.typemap:
            raise TypeError('duplicate registration')
        self.typemap[types] = func


def multimethod(*types):
    def register(func):
        func = getattr(func, "__lastreg__", func)
        name = func.__name__
        mm = registry.get(name)
        if mm is None:
            mm = registry[name] = MultiMethod(name)
        mm.register(types, func)
        mm.__lastreg__ = func
        return mm
    return register
