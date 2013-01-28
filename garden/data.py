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
    """
    I am a single piece of input data.
    
    See L{IInput} for a description of my attributes.
    """
    implements(IInput)



class Data(namedtuple('Data', ['entity', 'name', 'version', 'lineage', 'value'])):
    """
    I am a single piece of data.
    
    See L{IData} for a description of my attributes.
    """
    implements(IData)


def adaptInputToData(i):
    """
    Convert an L{IInput} into a L{Data}
    """
    return Data(i.entity, i.name, i.version, linealHash(i.name, i.version), i.value)
components.registerAdapter(adaptInputToData, IInput, IData)



class WorkInput(namedtuple('WorkInput', ['name', 'version', 'lineage', 'value', 'hash'])):
    """
    I am an input needed for work (I'm like L{Data} but with a hash).
    
    See L{IWorkInput} for a description of my attributes.
    """
    implements(IWorkInput)


def adaptDataToWorkInput(d):
    """
    Convert an L{IData} into a L{WorkInput}
    """
    return WorkInput(d.name, d.version, d.lineage, d.value, sha1(d.value).hexdigest())
components.registerAdapter(adaptDataToWorkInput, IData, IWorkInput)



class _Work(namedtuple('Work', ['entity', 'name', 'version', 'lineage', 'inputs'])):
    implements(IWork)



class Work(_Work):
    """
    I am a work request.
    
    See L{IWork} for a description of my attributes.
    """
    
    def __new__(cls, entity, name, version, lineage, inputs):
        return cls.__bases__[0].__new__(cls, entity, name, version, lineage,
                                        tuple([WorkInput(*x) for x in inputs]))


    def toResult(self, result):
        """
        Make an IResult out of this work and the result of the work
        """
        return Result(self.entity, self.name, self.version, self.lineage, result,
                      [IResultInput(x) for x in self.inputs])


    def toResultError(self, error):
        """
        Make an ResultError out of me, including the passed-in C{error}.
        """
        return ResultError(self.entity, self.name, self.version, self.lineage,
                           error, [IResultInput(x) for x in self.inputs])



class ResultInput(namedtuple('ResultInput', ['name', 'version', 'lineage', 'hash'])):
    """
    I am a partial input for including with results and error.  I'm like
    L{Data}, but without C{entity} and C{value}.
    """
    implements(IResultInput)



def adaptWorkInputToResultInput(i):
    """
    Convert an L{IWorkInput} to a L{ResultInput}
    """
    return ResultInput(i.name, i.version, i.lineage, i.hash)
components.registerAdapter(adaptWorkInputToResultInput, IWorkInput, IResultInput)



class _Result(namedtuple('Result', ['entity', 'name', 'version', 'lineage', 'value', 'inputs'])):
    implements(IResult)


class Result(_Result):
    """
    I am the result of some work.
    
    See L{IResult} for a description of my attributes.
    """
    
    def __new__(cls, entity, name, version, lineage, value, inputs):
        return cls.__bases__[0].__new__(cls, entity, name, version, lineage,
                                        value, tuple([ResultInput(*x) for x in inputs]))


def adaptResultToData(r):
    """
    Convert an L{IResult} to a L{Data}
    """
    return Data(r.entity, r.name, r.version, r.lineage, r.value)
components.registerAdapter(adaptResultToData, IResult, IData)

class _ResultError(namedtuple('ResultError', ['entity', 'name', 'version', 'lineage', 'error', 'inputs'])):
    implements(IResultError)


class ResultError(_ResultError):
    """
    I am a resulting error of some work.
    
    See L{IResultError} for a description of my attributes.
    """

    def __new__(cls, entity, name, version, lineage, value, inputs):
        return cls.__bases__[0].__new__(cls, entity, name, version, lineage,
                                        value, tuple([ResultInput(*x) for x in inputs]))


