Garden
======

Jorge Luis Borges wrote
[The Garden of Forking Paths](http://www.coldbacon.com/writing/borges-garden.html).
This project lets you create gardens of computing, forking paths.


How it works, through an example
--------------------------------

You are a teacher, and want to compute student's grades.  Assignments are worth
40% of the grade and exams 60%:

    def compute_grade_percent(assignment_percent, exam_percent):
        return (0.4 * assignment_percent) + (0.6 * exam_percent)

You want letter grades:

    def computer_letter_grade(grade_percent):
        if grade_precent > 0.9:
            return 'A'
        elif grade_precent > 0.8:
            return 'B'
        elif grade_percent > 0.7:
            return 'C'
        elif grade_percent > 0.6:
            return 'D'
        else:
            return 'F'





