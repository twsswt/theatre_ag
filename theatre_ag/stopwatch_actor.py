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

    def _issue_tick_to_parent_clock(self):

        time_period = self._calculate_next_time_period()

        for _ in range(0, time_period):
            if self.watched_clock.will_tick_again:
                self.idling.idle()
            else:
                self._parent_clock.max_ticks = self._parent_clock.current_tick
                break

        self._parent_clock.tick()

    def issue_tick(self):
        while self.watched_clock.will_tick_again:
            self._issue_tick_to_parent_clock()
        self._parent_clock.max_ticks = self._parent_clock.current_tick
        self._parent_clock.tick()


class StopwatchActor(TaskQueueActor):
    """
    An actor with the repeated task of tracking time on what clock to enable a tick on a parent clock.
    """

    def __init__(self, logical_name,  clock, parent_clock, granularity, precision=lambda granularity: granularity):
        super(StopwatchActor, self).__init__(f'stopwatch for {logical_name}', clock)
        stopwatch_worfklow = _StopwatchWorkflow(clock, parent_clock, granularity, precision)
        self.allocate_task(stopwatch_worfklow.issue_tick, stopwatch_worfklow)