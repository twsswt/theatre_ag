"""
@author twsswt
"""


class AllocatedTask(object):

    def __init__(self, workflow, entry_point, args):
        self.workflow = workflow
        self.entry_point = entry_point
        self.args = args

        self.completion_information = None

    def __repr__(self):
        return "t_(%s, %s)" % (str(self.entry_point), str(self.args))

    @property
    def completed(self):
        return self.completion_information is not None


class CompletedTask(object):

    def __init__(self, func, parent, start_tick):
        self.parent = parent
        self.sub_tasks = list()

        self.func = func
        self.start_tick = start_tick
        self.finish_tick = None

    def append_sub_task(self, sub_task):
        self.sub_tasks.append(sub_task)
        pass

    def __str__(self):
        return "%s(%d->%d)" % (self.func.func_name, self.start_tick, self.finish_tick)

    def __repr__(self):
        return self.__str__()
