import unittest

from theatre_ag import SynchronizingClock, StopwatchActor


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.seconds_clock = SynchronizingClock(max_ticks=300)
        self.minutes_clock = SynchronizingClock(max_ticks=5)
        self.stopwatch_actor = StopwatchActor(
            logical_name='SecondsToMinutes',
            clock=self.seconds_clock,
            parent_clock=self.minutes_clock,
            granularity=60)

        self.stopwatch_actor.start()

    def test_one_minute_tick_after_60_seconds(self):
        for second in range(0, 300):
            self.seconds_clock.tick()

        self.assertEqual(300, self.seconds_clock.current_tick)
        self.assertEqual(5, self.minutes_clock.current_tick)


if __name__ == '__main__':
    unittest.main()
