import unittest

from theatre_ag import SynchronizingClock, InterClockSynchronization, default_cost, TaskQueueActor


class ExampleWorkflow(object):

    is_workflow = True

    def __init__(self):
        pass

    @default_cost(1)
    def task_a(self):
        self.task_b()

    @default_cost(1)
    def task_b(self):
        pass


class TestInterClockSynchronizationWithActors(unittest.TestCase):
    def test_non_blocking_for_actors(self):
        seconds_clock = SynchronizingClock(max_ticks=3600)
        minutes_clock = SynchronizingClock()
        hours_clock = SynchronizingClock()

        seconds_clock.add_tick_listener(InterClockSynchronization(minutes_clock, granularity=60))
        minutes_clock.add_tick_listener(InterClockSynchronization(hours_clock, granularity=60))

        actor = TaskQueueActor(0, minutes_clock)
        example_workflow = ExampleWorkflow()

        actor.allocate_task(example_workflow.task_a, example_workflow)
        actor.initiate_shutdown()
        actor.start()

        while hours_clock.current_tick < 1:
            seconds_clock.tick()

        self.assertEqual(actor.last_task.finish_tick, 2)

        self.assertEqual(3600, seconds_clock.current_tick)
        self.assertEqual(60, minutes_clock.current_tick)
        self.assertEqual(1, hours_clock.current_tick)


if __name__ == '__main__':
    unittest.main()
