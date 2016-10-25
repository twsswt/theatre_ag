"""
@author Tim Storer
"""


from threading import Event


class AbstractClock(object):

    def __init__(self, max_ticks=1):
        self.max_ticks = max_ticks
        self.ticks = 0
        self.alarms = list()

    @property
    def current_tick(self):
        return self.ticks

    def _tick(self):
        self.ticks += 1
        self._check_alarms()

    def _check_alarms(self):
        for alarm in self.alarms:
            if alarm[0] <= self.ticks:
                alarm[1].set()

    def set_alarm (self, time):
        event = Event()
        alarm = (time, event)
        self.alarms.append(alarm)
        event.clear()
        event.wait()


class ManualClock(AbstractClock):

    def __init__(self, max_ticks=1):
        super(ManualClock, self).__init__(max_ticks)

    def tick(self):
        self._tick()


class SystemTimeClock(AbstractClock):

    def __init__(self, max_ticks=1):
        ManualClock.__init__(self, max_ticks)

