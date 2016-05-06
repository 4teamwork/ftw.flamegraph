from unittest import TestCase
from ftw.flamegraph.flamegraph import FlameGraph


class TestFlameGraph(TestCase):

    def test_1(self):
        stacks = [
            [
                ('/path/of/other_module.py', 3, 'methodname'),
                ('/path/of/module.py', 50, 'other_method'),
                ('/path/of/module.py', 12, 'methodname'),
            ],
            [
                ('/path/of/module.py', 50, 'other_method'),
                ('/path/of/module.py', 12, 'methodname'),
            ],
            [
                ('/path/of/other_module.py', 100, 'other_method'),
                ('/path/of/module.py', 12, 'methodname'),
            ],
        ]
        fg = FlameGraph(stacks)
