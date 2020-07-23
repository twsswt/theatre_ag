"""
@author twsswt
"""


class Cast(object):
    """
    A set of actors who synchronize their actions on a single clock.
    """

    def __init__(self, members=None):
        self.members = set(members) if members is not None else set()

    def add_member(self, actor):
        self.members.add(actor)

    def improvise(self, directions):
        directions.apply(self.members)

    def start(self):
        for actor in self.members:
            actor.start()

    def shutdown(self):
        """
        Ends the performance by the cast by first initiating the shutdown of all member actors and then waiting for
        their termination.  This method can be safely called when the cast's clock is executed in a separate thread to
        the call.  Otherwise, <code>initiate_shutdown</code> should be called first, then a clock tick issued,
        followed by <code>wait_for_shutdown</code>.
        """
        self.initiate_shutdown()
        self.wait_for_shutdown()

    def initiate_shutdown(self):
        """
        Notifies all actors in the cast to begin shutdown.
        """
        for actor in self.members:
            actor.initiate_shutdown()

    def wait_for_shutdown(self):
        """
        Waits for all actors in the cast to complete shutdown.
        """
        for actor in self.members:
            actor.wait_for_shutdown()

    @property
    def last_tick(self):
        return max(map(lambda m: m.last_tick, self.members))

    def task_count(self, task_filter):
        return sum(map(lambda actor: actor.task_count(task_filter), self.members))
