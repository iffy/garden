.. image:: https://travis-ci.org/iffy/garden.png?branch=master

`Builds <http://travis-ci.org/iffy/garden>`_ | `Docs <https://garden.readthedocs.org>`_


Garden
======

Jorge Luis Borges wrote `The Garden of Forking Paths
<http://www.coldbacon.com/writing/borges-garden.html>`_.
This project lets you create gardens of computing, forking paths.

Install it
----------

.. code:: bash

    git clone https://github.com/iffy/garden garden.git && cd garden.git
    python setup.py install


How it works, through an example
--------------------------------

You are a teacher, and want to compute students' grades.  Assignments are worth
40% of the grade and exams 60%.  You want letter grades too.  We'll use
``decimal.Decimal`` (imported as ``D``) instead of ``floats`` to avoid precision 
problems:

.. code:: python

    >>> from decimal import Decimal as D
    >>> def compute_percent(assignments, exams):
    ...    assignments = D(assignments)
    ...    exams = D(exams)
    ...    return str((D('0.4') * assignments) + (D('0.6') * exams))
    ...
    >>> def compute_letter(percent):
    ...     percent = D(percent)
    ...     if percent > D('0.9'):
    ...         return 'A'
    ...     elif percent > D('0.7'):
    ...         return 'B'
    ...     elif percent > D('0.6'):
    ...         return 'C'
    ...     elif percent > D('0.5'):
    ...         return 'D'
    ...     else:
    ...         return 'F'


Define how functions relate to each other by putting them in a ``Garden``.
This code adds a path for ``'percent'`` that depends on
``'assignments'`` and ``'exams'``.  The code also adds a path for
``'letter'`` which depends on ``'percent'`` (gloss over the ``'v1'``
strings for now -- they will be important later):

.. code:: python

    >>> from garden.path import Garden
    >>> garden = Garden()
    >>> garden.addPath('percent', 'v1', inputs=[
    ...     ('assignments', 'v1'),
    ...     ('exams', 'v1'),
    ... ])
    >>> garden.addPath('letter', 'v1', inputs=[
    ...     ('percent', 'v1'),
    ... ])


Get a ``Worker`` ready to do the computations by telling it which functions
correspond to which pieces of data:

.. code:: python

    >>> from garden.worker import BlockingWorker
    >>> worker = BlockingWorker()
    >>> worker.registerFunction('percent', 'v1', compute_percent)
    >>> worker.registerFunction('letter', 'v1', compute_letter)


Create a place to store the results:

.. code:: python

    >>> from garden.local import InMemoryStore
    >>> store = InMemoryStore()


Create a ``Gardener`` to coordinate work for the worker and tell them about
each other:

.. code:: python

    >>> from garden.gardener import Gardener
    >>> gardener = Gardener(garden, store, accept_all_lineages=True)
    >>> gardener.setWorkReceiver(worker)
    >>> worker.setResultReceiver(gardener)


Now give the ``Gardener`` some data about Frodo's progress in the class:


.. code:: python

    >>> gardener.inputReceived('Frodo', 'assignments', 'v1', '0.5')
    <Deferred...>

.. code:: python

    >>> gardener.inputReceived('Frodo', 'exams', 'v1', '0.9')
    <Deferred...>


And see that the grade was computed:

.. code:: python

    >>> store.get('Frodo', 'percent', 'v1').result
    [('Frodo', 'percent', 'v1', ... '0.74')]

.. code:: python

    >>> store.get('Frodo', 'letter', 'v1').result
    [('Frodo', 'letter', 'v1', ... 'B')]


Are you kidding me?
-------------------

That was way too much work.  Why would anyone want to use such a complicated
system to do what is essentially two function calls?

Because this is no ordinary garden,

.. epigraph::

    In all fictional works, each time a man is confronted with several
    alternatives, he chooses one and eliminates the others; in the fiction of
    Ts’ui Pên, he chooses -- simultaneously -- all of them. ...In the work of
    Ts’ui Pên, all possible outcomes occur.
    
    (The Garden of Forking Paths by Jorge Luis Borges)


Versions
--------

There's a mistake in the ``compute_letter`` function above: the cut-off for
B, C and D grades are 10% too low.  We want to fix this, but want to be able to
test our fix before we replace the buggy function.  Here's our fixed function:

.. code:: python

    >>> def compute_letter_v2(percent):
    ...     percent = D(percent)
    ...     if percent > D('0.9'):
    ...         return 'A'
    ...     elif percent > D('0.8'):
    ...         return 'B'
    ...     elif percent > D('0.7'):
    ...         return 'C'
    ...     elif percent > D('0.6'):
    ...         return 'D'
    ...     else:
    ...         return 'F'


Add the new function spec to the ``Garden``, with a distinct version:

.. code:: python

    >>> garden.addPath('letter', 'v2', inputs=[
    ...     ('percent', 'v1'),
    ... ])


Tell the worker about the new function:

.. code:: python

    >>> worker.registerFunction('letter', 'v2', compute_letter_v2)


Compute the result:

.. code:: python

    >>> gardener.doPossibleWork('Frodo', 'letter', 'v2')
    <Deferred...>


And see that Frodo now has two ``'letter'`` values:

.. code:: python

    >>> store.get('Frodo', 'letter', 'v1').result
    [('Frodo', 'letter', 'v1', ... 'B')]

.. code:: python

    >>> store.get('Frodo', 'letter', 'v2').result
    [('Frodo', 'letter', 'v2', ... 'C')]


More Versions
-------------

Suppose we are a terrible teacher and want to change the grade weighting
half way through the semester so that exams are 90% and assignments are 10%.
We make a new version of ``compute_percent``, add it to the ``Garden``
and tell the worker about it as before.  We also indicate that both
``'letter'`` functions can use this new ``'percent'`` as an input:

.. code:: python

    >>> def compute_percent_v2(assignments, exams):
    ...    assignments = D(assignments)
    ...    exams = D(exams)
    ...    return str((D('0.1') * assignments) + (D('0.9') * exams))
    ...
    >>> garden.addPath('percent', 'v2', inputs=[
    ...     ('assignments', 'v1'),
    ...     ('exams', 'v1'),
    ... ])
    >>> garden.addPath('letter', 'v1', inputs=[
    ...     ('percent', 'v2'),
    ... ])
    >>> garden.addPath('letter', 'v2', inputs=[
    ...     ('percent', 'v2'),
    ... ])
    >>> worker.registerFunction('percent', 'v2', compute_percent_v2)
    >>> gardener.doPossibleWork('Frodo', 'percent', 'v2')
    <Deferred...>


As you may expect, Frodo now has two versions of ``'percent'``:

.. code:: python

    >>> store.get('Frodo', 'percent', 'v1').result
    [('Frodo', 'percent', 'v1', ... '0.74')]

.. code:: python

    >>> store.get('Frodo', 'percent', 'v2').result
    [('Frodo', 'percent', 'v2', ... '0.86')]

And Frodo now has **four** versions of ``'letter'``:

.. code:: python

    >>> store.get('Frodo', 'letter', 'v1').result
    [('Frodo', 'letter', 'v1', ... 'B'), ('Frodo', 'letter', 'v1', ... 'B')]

.. code:: python

    >>> store.get('Frodo', 'letter', 'v2').result
    [('Frodo', 'letter', 'v2', ... 'C'), ('Frodo', 'letter', 'v2', ... 'B')]


Confused?  Enlightened?


Using/Deploying
===============

There are many ways to deploy components of the Garden.  Here are some:


Single Combination Process
--------------------------

You can start a single process containing both a Gardener and a single Worker
pretty easily.  Write a python module containing ``getWorker()``
and ``getGarden()`` functions, which return an ``IWorker`` and a ``Garden``
respectively.  Save the following as ``sample.py``:

.. code:: python

    # sample.py
    from garden.worker import ThreadedWorker
    from garden.path import Garden
    
    def cake(eggs, flour, flavor):
        words = []
        if flour == 'wheat':
            words.append('gross')
        return ' '.join(words + [flavor, 'cake'])
    
    def getGarden():
        garden = Garden()
        garden.addPath('cake', '1', [
            ('eggs', '1'),
            ('flour', '1'),
            ('flavor', '1'),
        ])
        return garden
    
    def getWorker():
        worker = ThreadedWorker()
        worker.registerFunction('cake', '1', cake)
        return worker
    
And then spawn a combo process with ``twistd``:

.. code:: bash

    twistd -n garden combo -m sample --sqlite-db=/tmp/data.sqlite -w tcp:9990


Data will be saved in ``/tmp/data.sqlite``.  New data values can be sent using
HTTP on port 9990.  (You can manually add data by visiting
http://127.0.0.1:9990/ and you can view a live feed of the results at http://127.0.0.1:9990/feed).

Load some data with ``curl``:

.. code:: bash

    curl -d 'entity=Gandalf' -d 'name=eggs' -d 'version=1' -d 'value=good' http://127.0.0.1:9990
    curl -d 'entity=Gandalf' -d 'name=flour' -d 'version=1' -d 'value=wheat' http://127.0.0.1:9990
    curl -d 'entity=Gandalf' -d 'name=flavor' -d 'version=1' -d 'value=hobbit' http://127.0.0.1:9990

And see the result:

.. code::

    $ sqlite3 /tmp/data.sqlite "select value from data where name='cake';"
    value               
    --------------------
    gross hobbit cake

Use better flour, and see the data change:

.. code:: bash

    curl -d 'entity=Gandalf' -d 'name=flour' -d 'version=1' -d 'value=white' http://127.0.0.1:9990

.. code::

    $ sqlite3 /tmp/data.sqlite "select value from data where name='cake';"
    value               
    --------------------
    hobbit cake 

