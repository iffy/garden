from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyClass, verifyObject


from garden.util import RoundRobinChooser



class RoundRobinChooserTest(TestCase):


    def test_basic(self):
        """
        You can add things to the list and cycle through them.
        """
        ch = RoundRobinChooser()
        ch.add('a')
        ch.add('b')
        ch.add('c')
        self.assertEqual(ch.next(), 'a')
        self.assertEqual(ch.next(), 'b')
        self.assertEqual(ch.next(), 'c')
        self.assertEqual(ch.next(), 'a')
        ch.add('d')
        self.assertEqual(ch.next(), 'b')
        self.assertEqual(ch.next(), 'c')
        self.assertEqual(ch.next(), 'd')


    def test_remove(self):
        """
        Removing things from the list should remove them immediately from the
        cycle.
        """
        ch = RoundRobinChooser()
        ch.add('a')
        ch.add('b')
        ch.add('c')
        self.assertEqual(ch.next(), 'a')
        self.assertEqual(ch.next(), 'b')
        ch.remove('c')
        self.assertEqual(ch.next(), 'a')
        ch.remove('a')
        self.assertEqual(ch.next(), 'b')
        self.assertEqual(ch.next(), 'b')


    def test_empty(self):
        """
        For now, an empty chooser raises an Exception to indicate nothing being
        available.
        """
        ch = RoundRobinChooser()
        self.assertRaises(Exception, ch.next)


