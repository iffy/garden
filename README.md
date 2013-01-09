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
>>> def compute_grade_percent(assignment_percent, exam_percent):
...    assignment_percent = D(assignment_percent)
...    exam_percent = D(exam_percent)
...    return (D('0.4') * assignment_percent) + (D('0.6') * exam_percent)
...
>>> def compute_letter_grade(grade_percent):
...     grade_percent = D(grade_percent)
...     if grade_precent > D('0.9'):
...         return 'A'
...     elif grade_precent > D('0.8'):
...         return 'B'
...     elif grade_percent > D('0.6'):
...         return 'C'
...     elif grade_percent > D('0.5'):
...         return 'D'
...     else:
...         return 'F'
```

Define how functions relate to each other by putting them in a `RecipeBook`.
This code adds a recipe for `'grade_percent'` that depends on
`'assignment_percent'` and `'exam_percent'`.  The code also adds a recipe for
`'letter_grade'` which depends on `'grade_percent'` (gloss over the `'version1'`
strings for now -- they will be important later):

```python
>>> from garden.recipe import RecipeBook
>>> recipe_book = RecipeBook()
>>> recipe_book.add('grade_percent', 'version1', args=[
...     ('assignment_percent', 'version1'),
...     ('exam_percent', 'version1'),
... ])
>>> recipe_book.add('letter_grade', 'version1', args=[
...     ('grade_percent', 'version1'),
... ])
```


Get a `Worker` ready to do the computations by telling it which functions
correspond to which pieces of data:

```python
>>> from garden.worker import Worker
>>> worker = Worker()
>>> worker.addFunction('grade_percent', 'version1', compute_grade_percent)
>>> worker.addFunction('letter_grade', 'version1', compute_letter_grade)
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
>>> garden = Garden(recipe_book, store, dispatcher)
```

Now give the `Garden` some data about Frodo's progress in the class (the last
arg is a JSON string:

```python
>>> garden.inputReceived('Frodo', 'assignment_percent', 'version1', '"0.5"')
>>> garden.inputReceived('Frodo', 'exam_percent', 'version1', '"0.9"')
```

And see that the grade was computed:

```python
>>> store.get('Frodo', 'grade_percent', 'version1')
[('Frodo', 'grade_percent', 'version1', ..., '"0.74"'))]
>>> store.get('Frodo', 'letter_grade', 'version1')
[('Frodo', 'letter_grade', 'version1', ..., 'C')
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
> (The Garden of Forking Paths by Jorge Luis Borges)

Function versions
-----------------

