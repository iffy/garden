from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyObject


from garden.interface import (IInput, IData, IWorkInput, IWork, IResultInput,
                              IResult, IResultError)
from garden.data import (Input, Data, WorkInput, Work, ResultInput, Result,
                         ResultError)



class InputTest(TestCase):


    def test_IInput(self):
        verifyObject(IInput, Input('joe', 'a', '1', 'value'))


    def test_basic(self):
        i = Input('joe', 'a', '1', 'value')
        self.assertEqual(i.entity, 'joe')
        self.assertEqual(i.name, 'a')
        self.assertEqual(i.version, '1')
        self.assertEqual(i.value, 'value')


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


