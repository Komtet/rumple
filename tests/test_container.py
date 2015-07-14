from unittest import TestCase

from rumple import Container, extend, share, value


class Service(object):
    def __init__(self, container):
        self.container = container


class Provider(object):
    @share()
    def service(self, container):
        return Service(container)

    @share()
    def service_for_extend(self, container):
        return Service(container)

    @value()
    def first_option(self):
        return 'value_1'

    @value('second_option_renamed')
    def second_option(self):
        return 'value_2'

    @value()
    def _ignored(self):
        return 'value'


class ExtendedProvider(object):
    @extend('service_for_extend')
    def extended_factory(self, service_for_extend, container):
        assert service_for_extend.container is container
        service_for_extend.container = 'new_container'
        return service_for_extend


class TestContainer(TestCase):
    def test_init_values(self):
        container = Container({'key': 'value'})
        self.assertEqual(container['key'], 'value')

    def test_register_service(self):
        container = Container()
        container['service'] = lambda c: Service(c)
        container['object'] = lambda: object()
        service = container['service']
        self.assertIsInstance(service, Service)
        self.assertIs(service, container['service'])
        self.assertIs(service.container, container)
        self.assertIs(container['object'].__class__, object)

    def test_register_option(self):
        container = Container()
        container['option'] = 'value'
        self.assertEqual(container['option'], 'value')

    def test_get_item_does_not_exists(self):
        container = Container()
        with self.assertRaises(KeyError) as cm:
            container.__getitem__('key')
        self.assertEqual(cm.exception.args, ('Item "key" does not exists.', ))

    def test_cannot_override_frozen_service(self):
        container = Container()
        container['service'] = lambda c: Service(c)
        container.__getitem__('service')
        with self.assertRaises(RuntimeError) as cm:
            container['service'] = None
        self.assertEqual(cm.exception.args, ('Cannot override frozen service "service".', ))

    def test_iter(self):
        container = Container()
        container['service'] = lambda c: Service(c)
        container['option'] = 'value'
        self.assertEqual(
            {key: val for key, val in container},
            {'service': container['service'], 'option': container['option']}
        )

    def test_contains(self):
        container = Container()
        container['option'] = 'value'
        self.assertNotIn('service', container)
        self.assertIn('option', container)

    def test_extend(self):
        container = Container()
        container['service'] = lambda c: Service(c)
        container['service_for_extend_without_container_1'] = lambda c: Service(c)
        container['service_for_extend_without_container_2'] = lambda: object()
        container['shared_service'] = lambda c: Service(c)
        container.__getitem__('shared_service')

        with self.assertRaises(TypeError) as cm:
            container.extend('service', None)
        self.assertEqual(cm.exception.args, ('Extended factory is not callable.', ))

        with self.assertRaises(KeyError) as cm:
            container.extend('non-existent', lambda: None)
        self.assertEqual(cm.exception.args, ('Item "non-existent" does not exists.', ))

        with self.assertRaises(RuntimeError) as cm:
            container.extend('shared_service', lambda: None)
        self.assertEqual(
            cm.exception.args,
            ('Unable to extend shared service "shared_service".', )
        )

        class ExtendedFactory(object):
            def __init__(self):
                self.container = None

            def __call__(self, service, c):
                service.container = 'new-container'
                self.container = c
                return service

        extended_factory = ExtendedFactory()
        container.extend('service', extended_factory)
        self.assertEqual(container['service'].container, 'new-container')
        self.assertIs(extended_factory.container, container)

        container.extend('service_for_extend_without_container_1', lambda service: str(service))
        self.assertIsInstance(container['service_for_extend_without_container_1'], str)

        container.extend('service_for_extend_without_container_2', lambda service: str(service))
        self.assertIsInstance(container['service_for_extend_without_container_2'], str)

    def test_register_provider(self):
        container = Container()
        provider = Provider()
        container.register(provider, {'additional_option': 'value'})
        container.register(ExtendedProvider())
        self.assertIsInstance(container['service'], Service)
        self.assertIsInstance(container['service_for_extend'], Service)
        self.assertEqual(container['first_option'], 'value_1')
        self.assertNotIn('second_option', container)
        self.assertEqual(container['second_option_renamed'], 'value_2')
        self.assertEqual(provider._ignored(), 'value')
        self.assertNotIn('_ignored', container)
        self.assertEqual(container['service_for_extend'].container, 'new_container')
