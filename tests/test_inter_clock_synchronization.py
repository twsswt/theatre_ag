import unittest

from theatre_ag import SynchronizingClock, InterClockSynchronization


class InterClockSynchronizationTestCase(unittest.TestCase):

    def test_one_minute_tick_after_60_seconds(self):
        seconds_clock = SynchronizingClock(max_ticks=60)
        minutes_clock = SynchronizingClock()

        seconds_clock.add_tick_listener(InterClockSynchronization(minutes_clock, granularity=60))

        while minutes_clock.current_tick < 1:
            seconds_clock.tick()

        self.assertEqual(60, seconds_clock.current_tick)
        self.assertEqual(1, minutes_clock.current_tick)

    def test_one_hour_tick_after_3600_seconds(self):
        seconds_clock = SynchronizingClock(max_ticks=3600)
        minutes_clock = SynchronizingClock()
        hours_clock = SynchronizingClock()

        seconds_clock.add_tick_listener(InterClockSynchronization(minutes_clock, granularity=60))
        minutes_clock.add_tick_listener(InterClockSynchronization(hours_clock, granularity=60))

        while hours_clock.current_tick < 1:
            seconds_clock.tick()

        self.assertEqual(3600, seconds_clock.current_tick)
        self.assertEqual(60, minutes_clock.current_tick)
        self.assertEqual(1, hours_clock.current_tick)

    def test_for_handling_imprecision(self):
        seconds_clock = SynchronizingClock(max_ticks=3600)
        minutes_clock = SynchronizingClock()
        hours_clock = SynchronizingClock()

        seconds_clock.add_tick_listener(InterClockSynchronization(minutes_clock, granularity=60))
        minutes_clock.add_tick_listener(
            InterClockSynchronization(hours_clock, granularity=60, precision=lambda granularity: granularity - 5))

        while hours_clock.current_tick < 1:
            seconds_clock.tick()

        self.assertEqual(3300, seconds_clock.current_tick)
        self.assertEqual(55, minutes_clock.current_tick)
        self.assertEqual(1, hours_clock.current_tick)


if __name__ == '__main__':
    unittest.main()
