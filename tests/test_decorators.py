from unittest import TestCase

from rumple import decorators


class TestDecorators(TestCase):
    def test_not_callable(self):
        for decorator in ['share', 'extend', 'value']:
            with self.assertRaises(TypeError) as cm:
                getattr(decorators, decorator)('key')(None)
            self.assertEqual(
                cm.exception.args,
                ('Object "None" is not callable.', )
            )

    def test_extend(self):
        extended_factory_default = decorators.extend()(lambda: None)
        extended_factory_key = decorators.extend('key')(lambda: None)
        self.assertEqual(
            getattr(extended_factory_default, decorators.Strategy.EXTEND),
            extended_factory_default.__name__
        )
        self.assertEqual(getattr(extended_factory_key, decorators.Strategy.EXTEND), 'key')

    def test_share(self):
        factory_default = decorators.share()(lambda: None)
        factory_key = decorators.share('key')(lambda: None)
        self.assertEqual(
            getattr(factory_default, decorators.Strategy.SHARE),
            factory_default.__name__
        )
        self.assertEqual(getattr(factory_key, decorators.Strategy.SHARE), 'key')

    def test_value(self):
        value_default = decorators.value()(lambda: None)
        value_key = decorators.value('key')(lambda: None)
        self.assertEqual(
            getattr(value_default, decorators.Strategy.VALUE),
            value_default.__name__
        )
        self.assertEqual(getattr(value_key, decorators.Strategy.VALUE), 'key')
