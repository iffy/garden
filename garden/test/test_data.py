from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyObject
from hashlib import sha1

from garden.interface import (IInput, IData, IWorkInput, IWork, IResultInput,
                              IResult, IResultError)
from garden.data import (Input, Data, WorkInput, Work, ResultInput, Result,
                         ResultError, linealHash)



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



class InputTest(TestCase):


    def test_IInput(self):
        verifyObject(IInput, Input('joe', 'a', '1', 'value'))


    def test_basic(self):
        i = Input('joe', 'a', '1', 'value')
        self.assertEqual(i.entity, 'joe')
        self.assertEqual(i.name, 'a')
        self.assertEqual(i.version, '1')
        self.assertEqual(i.value, 'value')


    def test_IData(self):
        """
        You can easily convert IInput into IData
        """
        i = Input('joe', 'a', '1', 'value')
        d = IData(i)
        self.assertEqual(d.entity, 'joe')
        self.assertEqual(d.name, 'a')
        self.assertEqual(d.version, '1')
        self.assertEqual(d.value, 'value')
        self.assertEqual(d.lineage, linealHash('a', '1'))


class DataTest(TestCase):


    def test_IData(self):
        verifyObject(IData, Data('joe', 'a', '1', 'xxxx', 'value'))


    def test_basic(self):
        d = Data('joe', 'a', '1', 'xxxx', 'value')
        self.assertEqual(d.entity, 'joe')
        self.assertEqual(d.name, 'a')
        self.assertEqual(d.version, '1')
        self.assertEqual(d.lineage, 'xxxx')
        self.assertEqual(d.value, 'value')


    def test_IWorkInput(self):
        """
        You can make it into a WorkInput
        """
        d = Data('joe', 'a', '1', 'xxxx', 'value')
        i = IWorkInput(d)
        self.assertEqual(i.name, 'a')
        self.assertEqual(i.version, '1')
        self.assertEqual(i.lineage, 'xxxx')
        self.assertEqual(i.value, 'value')
        self.assertEqual(i.hash, sha1('value').hexdigest())



class WorkInputTest(TestCase):


    def test_IWorkInput(self):
        verifyObject(IWorkInput, WorkInput('a', '1', 'xxxx', 'val', 'hash'))


    def test_attrs(self):
        i = WorkInput('a', '1', 'xxxx', 'val', 'hash')
        self.assertEqual(i.name, 'a')
        self.assertEqual(i.version, '1')
        self.assertEqual(i.lineage, 'xxxx')
        self.assertEqual(i.value, 'val')
        self.assertEqual(i.hash, 'hash')


    def test_IResultInput(self):
        """
        You can easily convert an IWorkInput to an IResultInput
        """
        i = WorkInput('a', '1', 'xxxx', 'val', 'hash')
        r = IResultInput(i)
        self.assertEqual(r.name, 'a')
        self.assertEqual(r.version, '1')
        self.assertEqual(r.lineage, 'xxxx')
        self.assertEqual(r.hash, 'hash')


    def test_computeHash(self):
        """
        If not provided, the hash should be computed.
        """
        i = WorkInput('a', '1', 'xxxx', 'val')
        self.assertEqual(i.hash, sha1('val').hexdigest())



class WorkTest(TestCase):


    def test_IWork(self):
        verifyObject(IWork, Work('bob', 'a', '1', 'xxxx', []))


    def test_attrs(self):
        w = Work('bob', 'a', '1', 'xxxx', [])
        self.assertEqual(w.entity, 'bob')
        self.assertEqual(w.name, 'a')
        self.assertEqual(w.version, '1')
        self.assertEqual(w.lineage, 'xxxx')
        self.assertEqual(w.inputs, (), "Should convert inputs to tuple")


    def test_inputs(self):
        """
        Initializing with tuples/lists/WorkInputs should work for the inputs
        argument.
        """
        w = Work('bob', 'a', '1', 'xxxx', [
            ('b', '1', 'xxxx', 'val', 'hash'),
            ['c', '1', 'xxxx', 'val', 'hash'],
            WorkInput('d', '1', 'xxxx', 'val', 'hash'),
        ])
        self.assertEqual(w.inputs, (
            WorkInput('b', '1', 'xxxx', 'val', 'hash'),
            WorkInput('c', '1', 'xxxx', 'val', 'hash'),
            WorkInput('d', '1', 'xxxx', 'val', 'hash'),
        ), "Should convert all arguments to a WorkInput")


    def test_toResult(self):
        """
        You can easily convert to a Result
        """
        w = Work('bob', 'a', '1', 'xxxx', [
            ('a', '1', 'xxxx', 'val', 'hash'),
        ])
        r = w.toResult('the result')
        self.assertEqual(r, Result('bob', 'a', '1', 'xxxx', 'the result', [
            ('a', '1', 'xxxx', 'hash'),
        ]))


    def test_toResultError(self):
        """
        You can convert to a ResultError
        """
        w = Work('bob', 'a', '1', 'xxxx', [
            ('a', '1', 'xxxx', 'val', 'hash'),
        ])
        r = w.toResultError('the err')
        self.assertEqual(r, ResultError('bob', 'a', '1', 'xxxx', 'the err', [
            ('a', '1', 'xxxx', 'hash'),
        ]))



class ResultInputTest(TestCase):


    def test_IResultInput(self):
        verifyObject(IResultInput, ResultInput('a', '1', 'xxxx', 'hash'))


    def test_attrs(self):
        i = ResultInput('a', '1', 'xxxx', 'hash')
        self.assertEqual(i.name, 'a')
        self.assertEqual(i.version, '1')
        self.assertEqual(i.lineage, 'xxxx')
        self.assertEqual(i.hash, 'hash')


class ResultTest(TestCase):


    def test_IResult(self):
        verifyObject(IResult, Result('bob', 'a', '1', 'xxxx', 'val', []))


    def test_attrs(self):
        r = Result('bob', 'a', '1', 'xxxx', 'val', [])
        self.assertEqual(r.entity, 'bob')
        self.assertEqual(r.name, 'a')
        self.assertEqual(r.version, '1')
        self.assertEqual(r.lineage, 'xxxx')
        self.assertEqual(r.value, 'val')
        self.assertEqual(r.inputs, (), "Should convert to tuple")


    def test_inputs(self):
        """
        Initializing with tuples/lists/ResultInputs should work for the inputs
        argument.
        """
        r = Result('bob', 'a', '1', 'xxxx', 'val', [
            ('b', '1', 'xxxx', 'hash'),
            ['c', '1', 'xxxx', 'hash'],
            ResultInput('d', '1', 'xxxx', 'hash'),
        ])
        self.assertEqual(r.inputs, (
            ResultInput('b', '1', 'xxxx', 'hash'),
            ResultInput('c', '1', 'xxxx', 'hash'),
            ResultInput('d', '1', 'xxxx', 'hash'),
        ), "Should convert all arguments to a ResultInput")


    def test_IData(self):
        """
        You can easily convert an IResult to IData
        """
        r = Result('bob', 'a', '1', 'xxxx', 'val', [])
        d = IData(r)
        self.assertEqual(d.entity, 'bob')
        self.assertEqual(d.name, 'a')
        self.assertEqual(d.version, '1')
        self.assertEqual(d.lineage, 'xxxx')
        self.assertEqual(d.value, 'val')



class ResultErrorTest(TestCase):


    def test_IResultError(self):
        verifyObject(IResultError, ResultError('bob', 'a', '1', 'xxxx', 'val', []))


    def test_attrs(self):
        r = ResultError('bob', 'a', '1', 'xxxx', 'val', [])
        self.assertEqual(r.entity, 'bob')
        self.assertEqual(r.name, 'a')
        self.assertEqual(r.version, '1')
        self.assertEqual(r.lineage, 'xxxx')
        self.assertEqual(r.error, 'val')
        self.assertEqual(r.inputs, (), "Should convert to tuple")


    def test_inputs(self):
        """
        Initializing with tuples/lists/ResultInputs should work for the inputs
        argument.
        """
        r = ResultError('bob', 'a', '1', 'xxxx', 'val', [
            ('b', '1', 'xxxx', 'hash'),
            ['c', '1', 'xxxx', 'hash'],
            ResultInput('d', '1', 'xxxx', 'hash'),
        ])
        self.assertEqual(r.inputs, (
            ResultInput('b', '1', 'xxxx', 'hash'),
            ResultInput('c', '1', 'xxxx', 'hash'),
            ResultInput('d', '1', 'xxxx', 'hash'),
        ), "Should convert all arguments to a ResultInput")


