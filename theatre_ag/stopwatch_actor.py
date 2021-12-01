from .actor import TaskQueueActor
from .workflow import Idling


class _StopwatchWorkflow:

    is_workflow = True

    def __init__(self, watched_clock, parent_clock, granularity, precision):
        self._parent_clock = parent_clock
        self._granularity = granularity
        self._precision = precision

        self.watched_clock = watched_clock

        self.idling = Idling()

    def _calculate_next_time_period(self):
        return max(self._precision(self._granularity), 1)

    def issue_tick_to_parent_clock(self, time_period):
        self.idling.idle_for(time_period)
        next_time_period = self._calculate_next_time_period()

        if not self.watched_clock.will_tick_another(next_time_period):
            self._parent_clock.max_ticks = self._parent_clock.current_tick + 1
        self._parent_clock.tick()

        return next_time_period

    def issue_tick(self):
        time_period = self._calculate_next_time_period()
        while self.watched_clock.will_tick_another(time_period):
            time_period = self.issue_tick_to_parent_clock(time_period)


class StopwatchActor(TaskQueueActor):
    """
    An actor with the repeated task of tracking time on what clock to enable a tick on a parent clock.
    """

    def __init__(self, logical_name,  clock, parent_clock, granularity, precision=lambda granularity: granularity):
        super(StopwatchActor, self).__init__(f'stopwatch for {logical_name}', clock)
        stopwatch_worfklow = _StopwatchWorkflow(clock, parent_clock, granularity, precision)
        self.allocate_task(stopwatch_worfklow.issue_tick, stopwatch_worfklow)