from twisted.trial.unittest import TestCase


from garden.garden import Garden


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