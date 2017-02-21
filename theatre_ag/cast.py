from .actor import Actor

class Cast(object):
    """
    A collection of actors who synchronize their actions on a single clock.
    """

    def __init__(self, clock):
        self.clock = clock

        self.members = list()

    def add_member(self, logical_name):
        actor = Actor(logical_name, self.clock)
        self.members.append(actor)
        return actor

    def start(self):
        for actor in self.members:
            actor.start()

    @property
    def last_tick(self):

        def finish_ticks(developer):
            if developer.last_completed_task is None:
                return 0
            elif developer.last_completed_task.finish_tick is None:
                return self.clock.current_tick
            else:
                return developer.last_completed_task.finish_tick

        last_tick = reduce(max, map(finish_ticks, self.members))

        return last_tick

    def task_count(self, task):
        return sum(map(lambda actor: actor.task_count(task), self.members))
