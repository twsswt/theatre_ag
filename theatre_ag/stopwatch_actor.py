from .actor import Actor
from .workflow import Idling
from .task import Task


class _StopwatchWorkflow:

    is_workflow = True

    def __init__(self, parent_clock, granularity, precision):
        self._parent_clock = parent_clock
        self._granularity = granularity
        self._precision = precision

        self.idling = Idling()

    def _calculate_next_time_period(self):
        return self._precision(self._granularity - 1)

    def issue_tick(self):
        time_period = self._calculate_next_time_period()
        self.idling.idle_for(time_period)
        self._parent_clock.tick()


class StopwatchActor(Actor):
    """
    An actor with the repeated task of tracking time on what clock to enable a tick on a parent clock.
    """

    def __init__(self, logical_name,  clock, parent_clock, granularity, precision=lambda granularity: granularity):
        super(StopwatchActor, self).__init__(logical_name, clock)
        self._stopwatch_worfklow = _StopwatchWorkflow(parent_clock, granularity, precision)

    def get_next_task(self):
        return Task(self._stopwatch_worfklow.issue_tick,  self._stopwatch_worfklow)

    def tasks_waiting(self):
        return True


