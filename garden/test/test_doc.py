from twisted.trial.unittest import TestCase
from twisted.python.filepath import FilePath
import doctest


_doctest_runner = doctest.DocTestRunner(verbose=False,
    optionflags=doctest.ELLIPSIS | doctest.IGNORE_EXCEPTION_DETAIL)
_doctest_parser = doctest.DocTestParser()



class ReadmeTest(TestCase):


    def test_readme(self):
        readme = FilePath(__file__).parent().parent().parent().child('README.rst')
        test = _doctest_parser.get_doctest(readme.getContent(), {},
                                           readme.basename(), readme.path, 0)
        output = []
        r = _doctest_runner.run(test, out=output.append)
        if r.failed:
            self.fail('%s\n%s' % (test.name, ''.join(output)))