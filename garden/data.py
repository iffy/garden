from collections import namedtuple
from garden.interface import (IInput, IData, IWorkInput, IWork, IResultInput,
                              IResult, IResultError)
from zope.interface import implements


class Input(namedtuple('Input', ['entity', 'name', 'version', 'value'])):
    implements(IInput)


class Data(namedtuple('Data', ['entity', 'name', 'version', 'lineage', 'value'])):
    implements(IData)


class WorkInput(namedtuple('WorkInput', ['name', 'version', 'lineage', 'value', 'hash'])):
    implements(IWorkInput)



class _Work(namedtuple('Work', ['entity', 'name', 'version', 'lineage', 'inputs'])):
    implements(IWork)


# XXX fake initializer... is there a better way to do this?
def Work(entity, name, version, lineage, inputs):
    return _Work(entity, name, version, lineage, tuple([WorkInput(*x) for x in inputs]))


class ResultInput(namedtuple('ResultInput', ['name', 'version', 'lineage', 'hash'])):
    implements(IResultInput)


class _Result(namedtuple('Result', ['entity', 'name', 'version', 'lineage', 'value', 'inputs'])):
    implements(IResult)


# XXX fake initializer... is there a better way to do this?
def Result(entity, name, version, lineage, value, inputs):
    return _Result(entity, name, version, lineage, value, tuple([ResultInput(*x) for x in inputs]))


class _ResultError(namedtuple('Result', ['entity', 'name', 'version', 'lineage', 'error', 'inputs'])):
    implements(IResultError)


# XXX fake initializer... is there a better way to do this?
def ResultError(entity, name, version, lineage, value, inputs):
    return _ResultError(entity, name, version, lineage, value, tuple([ResultInput(*x) for x in inputs]))
