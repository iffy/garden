Garden
======

Jorge Luis Borges wrote
[The Garden of Forking Paths](http://www.coldbacon.com/writing/borges-garden.html).
This project lets you create gardens of computing, forking paths.


How it works, through an example
--------------------------------

You are a teacher, and want to compute students' grades.  Assignments are worth
40% of the grade and exams 60%.  You want letter grades too:

```python
>>> from decimal import Decimal as D
>>> def compute_percent(assignments, exams):
...    assignments = D(assignments)
...    exams = D(exams)
...    return (D('0.4') * assignments) + (D('0.6') * exams)
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
```

Define how functions relate to each other by putting them in a `RecipeBook`.
This code adds a recipe for `'percent'` that depends on
`'assignments'` and `'exams'`.  The code also adds a recipe for
`'letter'` which depends on `'percent'` (gloss over the `'v1'`
strings for now -- they will be important later):

```python
>>> from garden.recipe import RecipeBook
>>> recipe_book = RecipeBook()
>>> recipe_book.add('percent', 'v1', args=[
...     ('assignments', 'v1'),
...     ('exams', 'v1'),
... ])
>>> recipe_book.add('letter', 'v1', args=[
...     ('percent', 'v1'),
... ])
```


Get a `Worker` ready to do the computations by telling it which functions
correspond to which pieces of data:

```python
>>> from garden.worker import Worker
>>> worker = Worker()
>>> worker.addFunction('percent', 'v1', compute_percent)
>>> worker.addFunction('letter', 'v1', compute_letter)
```

Create a place to store the results:

```python
>>> from garden.storage import InMemoryStore
>>> store = InMemoryStore()
```

Create a `Garden` to coordinate work for the `Worker`:

```python
>>> from garden.garden import Garden
>>> from garden.local import LocalWorkDispatcher
>>> dispatcher = LocalWorkDispatcher(worker)
>>> garden = Garden(recipe_book, store, dispatcher, accept_all_lineages=True)
```

Now give the `Garden` some data about Frodo's progress in the class (the last
arg is a JSON string):

```python
>>> garden.inputReceived('Frodo', 'assignments', 'v1', '"0.5"')
>>> garden.inputReceived('Frodo', 'exams', 'v1', '"0.9"')
```

And see that the grade was computed:

```python
>>> store.get('Frodo', 'percent', 'v1')
[('Frodo', 'percent', 'v1', ..., '"0.74"')]
>>> store.get('Frodo', 'letter', 'v1')
[('Frodo', 'letter', 'v1', ..., '"B"')]
```

Are you kidding me?
-------------------

That was way too much work.  Why would anyone want to use such a complicated
system to do what is essentially two function calls?

Because this is no ordinary garden,

> In all fictional works, each time a man is confronted with several
> alternatives, he chooses one and eliminates the others; in the fiction of
> Ts’ui Pên, he chooses -- simultaneously -- all of them. ...In the work of
> Ts’ui Pên, all possible outcomes occur.
> 
> (The Garden of Forking Paths by Jorge Luis Borges)

Versions
--------

There's a mistake in the `compute_letter` function above: the cut-off for
B, C and D grades are 10% too low.  We want to fix this, but want to be able to
test our fix before we replace the buggy function.  Here's our fixed function:

```python
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
```

Add the new function spec to the `RecipeBook`, with a distinct version:

```python
>>> recipe_book.add('letter', 'v2', args=[
...     ('percent', 'v1'),
... ])
```

Tell the worker about the new function:

```python
>>> worker.addFunction('letter', 'v2', compute_letter_v2)
```

Compute the function for all students (only Frodo's data has been added):

```python
>>> garden.forceCompute('letter', 'v2')
```

And see that Frodo now has two `'letter'` values:

```python
>>> store.get('Frodo', 'letter', 'v1')
[('Frodo', 'letter', 'v1', ..., '"B"')]
>>> store.get('Frodo', 'letter', 'v2')
[('Frodo', 'letter', 'v2', ..., '"C"')]
```

More Versions
-------------

Suppose we are a terrible teacher and want to change the grade weighting
half way through the semester so that exams are 90% and assignments are 10%.
We make a new version of `compute_percent`, add it to the `RecipeBook`
and tell the `worker` about it as before.  We also indicate that both
`'letter'` functions can use this new `'percent'` as an input:

```python
>>> def compute_percent_v2(assignments, exams):
...    assignments = D(assignments)
...    exams = D(exams)
...    return (D('0.1') * assignments) + (D('0.9') * exams)
...
>>> recipe_book.add('percent', 'v2', args=[
...     ('assignments', 'v1'),
...     ('exams', 'v1'),
... ])
>>> recipe_book.add('letter', 'v1', args=[
...     ('percent', 'v2'),
... ])
>>> recipe_book.add('letter', 'v2', args=[
...     ('percent', 'v2'),
... ])
>>> recipe_book.add('letter', 'v1
>>> worker.addFunction('percent', 'v2', compute_percent_v2)
>>> garden.forceCompute('percent', 'v2')
```

As you may expect, Frodo now has two versions of `'percent'`:

```python
>>> store.get('Frodo', 'percent', 'v1')
[('Frodo', 'percent', 'v1', ..., '"0.74"')]
>>> store.get('Frodo', 'percent', 'v2')
[('Frodo', 'percent', 'v2', ..., '"0.80"')]
```

And Frodo now has **four** versions of `'letter'`:

```python
>>> store.get('Frodo', 'letter', 'v1')
[('Frodo', 'letter', 'v1', ..., '"A"'),
('Frodo', 'letter', 'v1', ..., '"B"')]
>>> store.get('Frodo', 'letter', 'v2')
[('Frodo', 'letter', 'v2', ..., '"C"'),
('Frodo', 'letter', 'v2', ..., '"D"')]
```

Confused?  Enlightened?