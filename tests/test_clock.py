import unittest
from mock import Mock

from theatre_ag import SynchronizingClock

# noinspection PyProtectedMember
from threading import _Event


class ClockTestCase(unittest.TestCase):

    def setUp(self):
        self.clock = SynchronizingClock(max_ticks=2)

    def test_synchronization(self):

        self.tick_listener = Mock()
        self.tick_listener.waiting_for_tick = Mock(spec=_Event)

        self.clock.add_tick_listener(self.tick_listener)

        self.clock.tick()

        self.tick_listener.waiting_for_tick.wait.assert_called_once_with()
        self.tick_listener.notify_new_tick.assert_called_once_with()

    def test_clock_synchronization(self):

        peer_clock = SynchronizingClock(max_ticks=20)

        self.clock.synchronize_on(peer_clock, granularity=1)


if __name__ == '__main__':
    unittest.main()
