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
        self.func = func
        self.parent = parent
        self.start_tick = start_tick

        self.finish_tick = None
        self.sub_tasks = list()

    def append_sub_task(self, sub_task):
        self.sub_tasks.append(sub_task)
        pass

    def __str__(self):
        return "%s(%d->%s)" % (self.func.func_name, self.start_tick, str(self.finish_tick))

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, CompletedTask):
            return NotImplemented
        else:
            return self.func == other.func and \
                   self.parent == other.parent and \
                   self.start_tick == other.start_tick and \
                   self.finish_tick == other.finish_tick
