import unittest

from theatre_ag import SynchronizingClock, Cast, TaskQueueActor, Idling


class TeamTestCase(unittest.TestCase):

    def setUp(self):

        self.clock = SynchronizingClock(max_ticks=1)

        self.cast = Cast()

    def test_add_member(self):
        self.cast.add_member(TaskQueueActor('alice', self.clock))

        self.assertEqual(1, len(self.cast.members))

    def test_multiple_actors(self):

        for name in range(0, 10):
            _actor = TaskQueueActor(name, self.clock)
            self.cast.add_member(_actor)
            idle_task = Idling()
            _actor.allocate_task(idle_task.idle, idle_task)

        self.cast.initiate_shutdown()
        self.cast.start()
        self.clock.start()
        self.cast.wait_for_shutdown()

        for actor in self.cast.members:
            self.assertEqual('idle()[0->1]', str(actor.last_task))

    def test_multiple_starts(self):
        self.cast.add_member(TaskQueueActor('alice', self.clock))
        self.cast.start()
        self.cast.start()
        self.cast.initiate_shutdown()
        self.clock.tick()
        self.cast.wait_for_shutdown()


if __name__ == '__main__':
    unittest.main()
