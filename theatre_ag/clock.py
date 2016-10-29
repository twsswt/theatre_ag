"""
@author twsswt
"""


class SynchronizingClock(object):

    def __init__(self, max_ticks=1):
        self.max_ticks = max_ticks
        self._ticks = 0
        self.tick_listener = list()

    @property
    def current_tick(self):
        return self._ticks

    def add_tick_listener(self, listener):
        self.tick_listener.append(listener)

    def tick(self):

        # Issue a tick once all listeners are waiting for them.
        for tick_listener in self.tick_listener:
            tick_listener.waiting_for_tick.wait()

        self._ticks += 1
        for tick_listener in self.tick_listener:
            tick_listener.notify_new_tick()

    def tick_toc(self):
        while self.current_tick < self.max_ticks:
            self.tick()
