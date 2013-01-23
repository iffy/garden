from twisted.trial.unittest import TestCase
from hashlib import sha1


from garden.path import Garden, linealHash, CycleError


class GardenTest(TestCase):


    def test_addPath(self):
        """
        You can add paths to a Garden.
        """
        g = Garden()
        g.addPath('foo', 'v1', [
            ('bar', 'a'),
            ('cow', 'b'),
        ])
        self.assertEqual(list(g.pathsRequiring('bar', 'a')), [('foo', 'v1')])
        self.assertEqual(list(g.pathsRequiring('cow', 'b')), [('foo', 'v1')])
        self.assertEqual(list(g.inputsFor('foo', 'v1')), [
            [('bar', 'a'), ('cow', 'b')]
        ])


    def test_addPath_obviousCycle(self):
        """
        It's illegal to add a destination that depends directly on itself.
        """
        g = Garden()
        self.assertRaises(CycleError, g.addPath, 'foo', 'v1', [
            ('foo', 'v1'),
        ])


    def test_addPath_oneStepAwayCycle(self):
        """
        It's illegal to add a destination that depends on something that depends
        on the first.
        """
        g = Garden()
        g.addPath('chicken', 'v1', [
            ('egg', 'v1'),
        ])
        self.assertRaises(CycleError, g.addPath, 'egg', 'v1', [
            ('chicken', 'v1'),
        ])


    def test_addPath_distantCycle(self):
        """
        It's illegal to create a cycle, even if the paths are far removed.
        """
        g = Garden()
        g.addPath('a', 'v1', [
            ('b', 'v1'),
        ])
        g.addPath('b', 'v1', [
            ('c', 'v1'),
        ])
        self.assertRaises(CycleError, g.addPath, 'c', 'v1', [
            ('a', 'v1'),
        ])


    def test_addPath_addCycleInMiddle(self):
        """
        Adding a path in the middle that will cause a Cycle should be detected
        """
        # a --> b --> c --> d --> a
        # add b --> c last
        g = Garden()
        g.addPath('d', 'v1', [
            ('c', 'v1'),
        ])
        g.addPath('b', 'v1', [
            ('a', 'v1'),
        ])
        g.addPath('a', 'v1', [
            ('d', 'v1'),
        ])
        self.assertRaises(CycleError, g.addPath, 'c', 'v1', [
            ('b', 'v1'),
        ])



class linealHashTest(TestCase):


    def test_basic(self):
        """
        The most basic lineal hash is SHA(SHA(name) + version)
        """
        a = linealHash('name', 'version')
        expected = sha1(sha1('name').hexdigest() + 'version').hexdigest()
        self.assertEqual(a, expected)


    def test_args(self):
        """
        If a data point has inputs, the lineal hash of the data point is
        SHA(SHA(SHA(name) + version) + input1_lineal_hash + input2_lineal_hash)
        """
        sample_hash1 = sha1('foo').hexdigest()
        sample_hash2 = sha1('bar').hexdigest()
        
        a = linealHash('name', 'version', [sample_hash1, sample_hash2])
        expected = sha1(linealHash('name', 'version') + sample_hash1 \
                        + sample_hash2).hexdigest()
        self.assertEqual(a, expected, "With inputs, expected lineal hash to be"
                         " H(linealHash + input1hash + input2hash)")


