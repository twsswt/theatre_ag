import unittest
from unittest.mock import Mock

from theatre_ag import SynchronizingClock

# noinspection PyProtectedMember
from threading import Event


class ClockTestCase(unittest.TestCase):

    def test_synchronization(self):
        self.clock = SynchronizingClock(max_ticks=2)

        self.tick_listener = Mock()
        self.tick_listener.waiting_for_tick = Mock(spec=Event)

        self.clock.add_tick_listener(self.tick_listener)

        self.clock.tick()

        self.tick_listener.waiting_for_tick.wait.assert_called_once_with()
        self.tick_listener.notify_new_tick.assert_called_once_with()

    def test_ticks_until_stopped(self):
        self.clock = SynchronizingClock()
        self.clock.tick()
        self.clock.tick()
        self.clock.issue_ticks = False
        self.clock.tick()
        self.assertEqual(self.clock.current_tick, 2)


if __name__ == '__main__':
    unittest.main()
