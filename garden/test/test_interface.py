from twisted.trial.unittest import TestCase
from zope.interface import Interface, implements


from garden.interface import ISourceable, ISource


class IFoo(Interface): pass
class IBar(Interface): pass


class Foo:
    implements(ISourceable)
    
    sourceInterfaces = (IFoo, IBar)



class adaptISourceableToISourceTest(TestCase):


    def test_basic(self):
        """
        You can turn an ISourceable into an ISource
        """
        foo = Foo()
        source = ISource(foo)
        self.assertEqual(source.interfaces, set([IFoo, IBar]))
        source.receivers['foo'] = 'something'
        s2 = ISource(foo)
        self.assertEqual(source, s2, "Should return the same ISource every"
                         " time")


