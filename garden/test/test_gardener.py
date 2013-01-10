from twisted.trial.unittest import TestCase


from garden.gardener import Gardener



class GardenerTest(TestCase):


    def test_init(self):
        """
        You can initialize with some things a Gardener needs.
        """
        g = Gardener('garden', 'store', 'dispatcher', accept_all_lineages=True)
        self.assertEqual(g.garden, 'garden')
        self.assertEqual(g.store, 'store')
        self.assertEqual(g.dispatcher, 'dispatcher')
        self.assertEqual(g.accept_all_lineages, True)