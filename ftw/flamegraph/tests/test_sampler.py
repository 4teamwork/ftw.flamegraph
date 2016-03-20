from unittest import TestCase
from ftw.flamegraph.testing import FLAMEGRAPH_INTEGRATION_TESTING
from ftw.flamegraph.sampler import Sampler
import time


class TestInstall(TestCase):
    layer = FLAMEGRAPH_INTEGRATION_TESTING

    def test_sampler_initalization(self):
        from ftw.flamegraph import sampler
        self.assertIsNotNone(sampler)


class TestSampler(TestCase):

    def test_sampling(self):
        def function(end):
            while time.time() < end:
                pass
        sampler = Sampler()
        sampler.start()
        function(time.time() + 0.01)
        sampler.stop()
        self.assertGreater(len(sampler.stacks), 0)
        self.assertEqual('function', sampler.stacks[0][0][2])

    def test_folded_stacks_output(self):
        sampler = Sampler()
        sampler.stacks = [[
            ('/path/of/module.py', 12, 'methodname'),
            ('/path/of/module.py', 50, 'other_method'),
            ('/path/of/other_module.py', 3, 'methodname'),
        ]]
        self.assertEqual(
            'methodname (/path/of/other_module.py:3);'
            'other_method (/path/of/module.py:50);'
            'methodname (/path/of/module.py:12) 1\n', sampler.folded_stacks())
