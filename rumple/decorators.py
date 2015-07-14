from collections import namedtuple

__all__ = ['Strategy', 'extend', 'share', 'value']

Strategy = namedtuple('Strategy', ('SHARE', 'EXTEND', 'VALUE'))
Strategy = Strategy('ctr_share', 'ctr_extend', 'ctr_val')


def _decorator(strategy):
    def init(key):
        def decorator(method):
            if not callable(method):
                raise TypeError('Object "{0}" is not callable.'.format(method))
            setattr(method, strategy, key if key else method.__name__)
            return method
        return decorator
    return init


def extend(key=None):
    return _decorator(Strategy.EXTEND)(key)


def share(key=None):
    return _decorator(Strategy.SHARE)(key)


def value(key=None):
    return _decorator(Strategy.VALUE)(key)
