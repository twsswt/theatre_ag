import unittest

from theatre_ag import SynchronizingClock, StopwatchActor


class StopwatchActorTestCase(unittest.TestCase):

    def test_one_minute_tick_after_60_seconds(self):
        seconds_clock = SynchronizingClock(max_ticks=60)
        minutes_clock = SynchronizingClock()

        stopwatch_actor = StopwatchActor(
            logical_name='seconds_to_minutes',
            clock=seconds_clock,
            parent_clock=minutes_clock,
            granularity=60)

        stopwatch_actor.start()
        for second in range(0, 60):
            seconds_clock.tick()
        seconds_clock.tick()

        # Ensure final tick is released to parent clock before testing state.
        stopwatch_actor.shutdown()

        self.assertEqual(60, seconds_clock.current_tick)
        self.assertEqual(1, minutes_clock.current_tick)

    def test_one_hour_tick_after_3600_seconds(self):
        seconds_clock = SynchronizingClock(max_ticks=3600)
        minutes_clock = SynchronizingClock()
        hours_clock = SynchronizingClock()

        minutes_stopwatch_actor = StopwatchActor(
            logical_name='seconds_to_minutes',
            clock=seconds_clock,
            parent_clock=minutes_clock,
            granularity=60)

        hours_stopwatch_actor = StopwatchActor(
            logical_name='minutes_to_hours',
            clock=minutes_clock,
            parent_clock=hours_clock,
            granularity=60)

        minutes_stopwatch_actor.start()
        hours_stopwatch_actor.start()

        for second in range(0, 3600):
            seconds_clock.tick()

        # Ensure final ticks are released to parent clock before testing state.
        minutes_stopwatch_actor.initiate_shutdown()
        hours_stopwatch_actor.initiate_shutdown()
        minutes_stopwatch_actor.wait_for_shutdown()
        hours_stopwatch_actor.wait_for_shutdown()

        self.assertEqual(3600, seconds_clock.current_tick)
        self.assertEqual(60, minutes_clock.current_tick)
        self.assertEqual(1, hours_clock.current_tick)

    def test_30_minutes_and_0_hour_tick_after_1800_seconds(self):
        seconds_clock = SynchronizingClock(max_ticks=3600)
        minutes_clock = SynchronizingClock()
        hours_clock = SynchronizingClock()

        minutes_stopwatch_actor = StopwatchActor(
            logical_name='seconds_to_minutes',
            clock=seconds_clock,
            parent_clock=minutes_clock,
            granularity=60)

        hours_stopwatch_actor = StopwatchActor(
            logical_name='minutes_to_hours',
            clock=minutes_clock,
            parent_clock=hours_clock,
            granularity=60)

        minutes_stopwatch_actor.start()
        hours_stopwatch_actor.start()

        for second in range(0, 1800):
            seconds_clock.tick()
        seconds_clock.shutdown()

        # Ensure final ticks are released to parent clock before testing state.
        minutes_stopwatch_actor.initiate_shutdown()
        hours_stopwatch_actor.initiate_shutdown()
        minutes_stopwatch_actor.wait_for_shutdown()
        hours_stopwatch_actor.wait_for_shutdown()

        self.assertEqual(1800, seconds_clock.current_tick)
        self.assertEqual(30, minutes_clock.current_tick)
        self.assertEqual(0, hours_clock.current_tick)


if __name__ == '__main__':
    unittest.main()
