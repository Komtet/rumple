======
Rumple
======

Simple Dependency Injection Container inspired by `Pimple <http://pimple.sensiolabs.org/>`_.

.. image:: https://img.shields.io/travis/Komtet/rumple.svg?style=flat-square
    :target: https://travis-ci.org/Komtet/rumple

Installation
============

Using pip:

.. code:: sh

    # pip install rumple

Manually:

.. code:: sh

    $ git clone https://github.com/Komtet/rumple
    $ cd rumple
    # python setup.py install

Usage
=====

.. code:: python

    from rumple import Container

    c1 = Container()
    c2 = Container({
        'param': 'value',
        'service': lambda: object()
    })


Defining services
-----------------

.. code:: python

    from rumple import Container


    class Service(object):
        pass


    class AnotherService(object):
        def __init__(self, service):
            self.service = service

    container = Container()
    container['service'] = lambda: Service()
    container['another_service'] = lambda c: AnotherService(c['service'])
    another_service = container['another_service']
    assert isinstance(another_service, AnotherService)
    assert another_service.service is container['service']

Defining parameters
-------------------

.. code:: python

    from rumple import Container

    container = Container()
    container['parameter'] = 'value'
    assert container['parameter'] == 'value'

Extending services
------------------

.. code:: python

    from rumple import Container


    class Service(object):
        def __init__(self):
            self.optional_dependency = None

        def set_optional_dependency(self, dependency):
            self.optional_dependency = dependency


    class OptionalDependency(object):
        pass


    def extend_service(service, container):  # Note: you can omit "container" argument
        service.set_optional_dependency(container['optional_dependency'])
        return service

    container = Container()
    container['service'] = lambda: Service()
    container['optional_dependency'] = lambda: OptionalDependency()
    container.extend('service', extend_service)

Providers
---------

.. code-block:: python

    from rumple import Container, extend, share, value


    class Provider(object):
        @share()
        def service(self):
            return object()

        @share('renamed_service')
        def another_service(self):
            return object()

        @share()
        def service_for_extend(self):
            return object()

        @value()
        def first_option(self):
            return 'value_1'

        @value('second_option_renamed')
        def second_option(self):
            return 'value_2'

        @value()
        def _ignored(self):
            return 'value'


    class AnotherProvider(object):
        @extend('service_for_extend')
        def extend_service(self, service_for_extend):
            assert isinstance(service_for_extend, object)
            return str(object)

    class SomeLibProvider(object):
        __prefix__ = 'some_lib.'

        @share()
        def service(self):
            return object()

        @extend('some_lib.service')
        def extend(self, service):
            return str(service)


    container = Container()
    container.register(Provider())
    container.register(AnotherProvider(), {'additional_option': 'value1'})
    container.register(SomeLibProvider(), {'additional_option': 'value2'})
    assert isinstance(container['service'], object)
    assert isinstance(container['renamed_service'], object)
    assert isinstance(container['service_for_extend'], str)
    assert container['first_option'] == 'value_1'
    assert container['second_option_renamed'] == 'value_2'
    assert '_ignored' not in container
    assert container['additional_option'] == 'value1'
    assert isinstance(container['some_lib.service'], str)
    assert container['some_lib.additional_option'] == 'value2'

Iterating through a container
-----------------------------

.. code:: python

    from rumple import Container

    container = Container({'k1': 'v1', 'k2': 'v2'})
    for item in container:
        print(item)

    # Output:
    # ('k1', 'v1')
    # ('k2', 'v2')

Changelog
=========

0.2.0 (xx.xx.xxxx)
------------------

- Ablity to specify vendor prefix in providers.

0.1.0 (15.07.2015)
------------------

- First release

Contributing
============

- Fork and clone it
- Create your feature branch (git checkout -b awesome-feature)
- Make your changes
- Write/update tests, if it's necessary
- Update README.md, if it's necessary
- Push your branch (git push origin awesome-feature)
- Send a pull request

LICENSE
=======

The MIT License (MIT)
