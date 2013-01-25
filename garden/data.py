from collections import namedtuple
from garden.interface import (IInput, IData, IWorkInput, IWork, IResultInput,
                              IResult, IResultError)
from zope.interface import implements
from twisted.python import components
from hashlib import sha1



def linealHash(name, version, input_hashes=None):
    """
    Compute a hash to describe the lineage of a particular garden destination.
    
    @param name: Destination name
    @param version: Destination version
    
    @param input_hashes: If the data point identified by the C{name}, C{version}
        pair is a destination of a garden path, then C{input_hashes} is the
        list of lineal hashes of the garden path's inputs.  For instance, if
        this garden path was defined::
        
            garden.addPath('cake', '1', [
                ('eggs', '1'),
                ('flour', '1'),
            ])
        
        And both C{('eggs', '1')} and C{('flour', '1')} do not require any
        inputs, then to compute the lineal hash of C{('cake', '1')}, do this::
        
            linealHash('cake', '1', [
                linealHash('eggs', '1'),
                linealHash('flour', '1'),
            ])
        
        If C{('flour', '1')} required input C{('wheat', '1')} then you would
        instead do this::
        
            linealHash('cake', '1', [
                linealHash('eggs', '1'),
                linealHash('flour', '1', [
                    linealHash('wheat', '1'),
                ]),
            ])
    """
    basic = sha1(sha1(name).hexdigest() + version).hexdigest()
    if not input_hashes:
        return basic
    
    # destination has inputs
    parts = [basic] + input_hashes
    return sha1(''.join(parts)).hexdigest()




class Input(namedtuple('Input', ['entity', 'name', 'version', 'value'])):
    implements(IInput)





class Data(namedtuple('Data', ['entity', 'name', 'version', 'lineage', 'value'])):
    implements(IData)


def adaptInputToData(i):
    """
    Convert an L{IInput} into a L{Data}
    """
    return Data(i.entity, i.name, i.version, linealHash(i.name, i.version), i.value)
components.registerAdapter(adaptInputToData, IInput, IData)



class WorkInput(namedtuple('WorkInput', ['name', 'version', 'lineage', 'value', 'hash'])):
    implements(IWorkInput)


def adaptDataToWorkInput(d):
    """
    Convert an L{IData} into a L{WorkInput}
    """
    return WorkInput(d.name, d.version, d.lineage, d.value, sha1(d.value).hexdigest())
components.registerAdapter(adaptDataToWorkInput, IData, IWorkInput)


class _Work(namedtuple('Work', ['entity', 'name', 'version', 'lineage', 'inputs'])):
    implements(IWork)


# XXX fake initializer... is there a better way to do this?
def Work(entity, name, version, lineage, inputs):
    return _Work(entity, name, version, lineage, tuple([WorkInput(*x) for x in inputs]))


class ResultInput(namedtuple('ResultInput', ['name', 'version', 'lineage', 'hash'])):
    implements(IResultInput)


def adaptWorkInputToResultInput(i):
    """
    Convert an L{IWorkInput} to a L{ResultInput}
    """
    return ResultInput(i.name, i.version, i.lineage, i.hash)
components.registerAdapter(adaptWorkInputToResultInput, IWorkInput, IResultInput)


class _Result(namedtuple('Result', ['entity', 'name', 'version', 'lineage', 'value', 'inputs'])):
    implements(IResult)


# XXX fake initializer... is there a better way to do this?
def Result(entity, name, version, lineage, value, inputs):
    return _Result(entity, name, version, lineage, value, tuple([ResultInput(*x) for x in inputs]))


def adaptResultToData(r):
    """
    Convert an L{IResult} to a L{Data}
    """
    return Data(r.entity, r.name, r.version, r.lineage, r.value)
components.registerAdapter(adaptResultToData, IResult, IData)

class _ResultError(namedtuple('Result', ['entity', 'name', 'version', 'lineage', 'error', 'inputs'])):
    implements(IResultError)


# XXX fake initializer... is there a better way to do this?
def ResultError(entity, name, version, lineage, value, inputs):
    return _ResultError(entity, name, version, lineage, value, tuple([ResultInput(*x) for x in inputs]))


