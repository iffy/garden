from twisted.trial.unittest import TestCase
from hashlib import sha1


from garden.garden import Garden, linealHash


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


