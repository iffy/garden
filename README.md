Garden
======

Jorge Luis Borges wrote
[The Garden of Forking Paths](http://www.coldbacon.com/writing/borges-garden.html).
This project lets you create gardens of computing, forking paths.


How it works, through an example
--------------------------------

You are a teacher, and want to compute student's grades.  Assignments are worth
40% of the grade and exams 60%:

```python
from decimal import Decimal as D

def compute_grade_percent(assignment_percent, exam_percent):
    return (D('0.4') * assignment_percent) + (D('0.6') * exam_percent)
```

In addition to percentages, you want letter grades for each student:

```python
def compute_letter_grade(grade_percent):
    if grade_precent > D('0.9'):
        return 'A'
    elif grade_precent > D('0.8'):
        return 'B'
    elif grade_percent > D('0.6'):
        return 'C'
    elif grade_percent > D('0.5'):
        return 'D'
    else:
        return 'F'
```

Define how functions relate to each other by putting them in a `RecipeBook`.
This code adds a recipe for `'grade_percent'` that depends on
`'assignment_percent'` and `'exam_percent'`.  The code also adds a recipe for
`'letter_grade'` that depends on `'grade_percent'`:

```python
from garden.recipe import RecipeBook

recipe_book = RecipeBook()
recipe_book.add('grade_percent', 'version1', args=[
    ('assignment_percent', 'version1'),
    ('exam_percent', 'version1'),
])
recipe_book.add('letter_grade', 'version1', args=[
    ('grade_percent', 'version1'),
])
```


Get a `Worker` ready to do the computations by telling it which functions
correspond to which pieces of data:

```python
from garden.worker import Worker

worker = Worker()
worker.addFunction('grade_percent', 'version1', compute_grade_percent)
worker.addFunction('letter_grade', 'version1', compute_letter_grade)
```

Create a `Garden` for to coordinate work for the `Worker`:

```python
from garden.garden import Garden
from garden.local import LocalWorkDispatcher

dispatcher = LocalWorkDispatcher(worker)
garden = Garden(recipe_book=recipe_book, work_dispatcher=dispatcher)
```    