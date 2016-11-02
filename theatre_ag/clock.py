"""
@author twsswt
"""


class SynchronizingClock(object):

    def __init__(self, max_ticks=1):
        self.max_ticks = max_ticks
        self._ticks = 0
        self.tick_listeners = list()

    @property
    def current_tick(self):
        return self._ticks

    def add_tick_listener(self, listener):
        self.tick_listeners.append(listener)

    def remove_tick_listener(self, listener):
        self.tick_listeners.remove(listener)

    def tick(self):
        print self.current_tick
        # Issue a tick once all listeners are waiting for them.
        for tick_listener in self.tick_listeners:
            tick_listener.waiting_for_tick.wait()
        self._ticks += 1

        for tick_listener in self.tick_listeners:
            tick_listener.notify_new_tick()

    def tick_toc(self):
        while self.current_tick < self.max_ticks:
            self.tick()
