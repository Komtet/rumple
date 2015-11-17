import inspect

from rumple.decorators import Strategy

__all__ = ['Container']


class Container(object):
    def __init__(self, values=None):
        self.__keys = []
        self.__factories = {}
        self.__frozen = {}
        self.__shared = {}
        if values is not None:
            for key, value in values.items():
                self[key] = value

    def __setitem__(self, key, value):
        if key in self.__frozen:
            raise RuntimeError('Cannot override frozen service "{0}".'.format(key))
        self.__keys.append(key)
        if callable(value):
            self.__factories[key] = value
        else:
            self.__shared[key] = value

    def __getitem__(self, key):
        if key not in self.__keys:
            raise KeyError('Item "{0}" does not exists.'.format(key))
        if key not in self.__shared:
            factory = self.__factories[key]
            if _is_factory_takes_container(factory):
                self.__shared[key] = factory(self)
            else:
                self.__shared[key] = factory()
        if key not in self.__frozen:
            self.__frozen[key] = True
        return self.__shared[key]

    def __iter__(self):
        for key in self.__keys:
            yield (key, self[key])

    def __contains__(self, key):
        return key in self.__keys

    def extend(self, key, extended_factory):
        if not callable(extended_factory):
            raise TypeError('Extended factory is not callable.')
        if key not in self.__factories:
            raise KeyError('Item "{0}" does not exists.'.format(key))
        if key in self.__shared:
            raise RuntimeError('Unable to extend shared service "{0}".'.format(key))
        factory = self.__factories[key]

        def new_factory(c):
            if _is_factory_takes_container(factory):
                service = factory(c)
            else:
                service = factory()
            args = [service]
            if _is_extended_factory_takes_container(extended_factory):
                args.append(c)
            return extended_factory(*args)

        self.__factories[key] = new_factory

    def register(self, provider, values=None):
        prefix = getattr(provider, '__prefix__', '') + '{0}'
        for attr in filter(lambda x: not x.startswith('_'), dir(provider)):
            attr = getattr(provider, attr)
            if hasattr(attr, Strategy.SHARE):
                self[prefix.format(getattr(attr, Strategy.SHARE))] = attr
            elif hasattr(attr, Strategy.EXTEND):
                self.extend(getattr(attr, Strategy.EXTEND), attr)
            elif hasattr(attr, Strategy.VALUE):
                self[prefix.format(getattr(attr, Strategy.VALUE))] = attr()
        if isinstance(values, dict):
            for key, value in values.items():
                self[prefix.format(key)] = value


def _is_factory_takes_container(factory):
    return _whether_takes_container(factory, 1)


def _is_extended_factory_takes_container(factory):
    return _whether_takes_container(factory, 2)


def _whether_takes_container(factory, num_args):
    if not inspect.isfunction(factory) and not inspect.ismethod(factory):
        to_inspect = factory.__call__
    else:
        to_inspect = factory
    total_args = len(inspect.getargspec(to_inspect).args)
    is_method = inspect.ismethod(to_inspect)
    return (
        (is_method and total_args == num_args + 1) or
        (not is_method and total_args == num_args)
    )
