class InterClockSynchronization:

    def __init__(self, parent, granularity=1, precision=lambda granularity: granularity):
        self._parent = parent
        self._granularity = granularity
        self._precision = precision

        self._count_down = self._next_time_period()

    def _next_time_period(self):
        return max(self._precision(self._granularity), 1)

    def wait_for_tick(self):
        pass

    def notify_new_tick(self):
        self._count_down -= 1
        if self._count_down <= 0:
            self._count_down = self._next_time_period()
            self._parent.tick()
