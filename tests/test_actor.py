from mock import Mock
from unittest import TestCase

from threading import Thread

from theatre_ag import Actor, AbstractClock


class ActorTestCase(TestCase):

    def setUp(self):

        self.clock = Mock(spec=AbstractClock)

        self.actor = Actor("alice", self.clock)

    def test_idle(self):
        self.clock.current_tick = 0
        self.actor.add_to_task_queue(Actor.idle, [])
        self.clock.current_tick = 1
        self.actor.start()
        self.actor.shutdown()

        self.assertEquals(True, True)

    def test_nested_task(self):

        def task_a(self):
            self.perform_task(task_b, [])

        def task_b(self):
            self.perform_task(Actor.idle)

        self.clock.current_tick = 0
        self.actor.add_to_task_queue(task_a, [])
        self.clock.current_tick = 1
        self.actor.start()
        self.actor.shutdown()

        self.assertEquals(True, True)

