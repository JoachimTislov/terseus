"""
This is a hand-written, ordinary Python library -- exactly what a developer
would bootstrap for their chosen target once, the traditional way. Nothing
here is generated. The schema's job is only to WIRE keywords to functions
like these, not to reimplement their logic.
"""


def mark_task_done(task):
    task.done = True


def set_task_owner(task, user):
    task.owner = user
