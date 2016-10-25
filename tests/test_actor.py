from mock import Mock
from unittest import TestCase

from threading import Thread

import inspect

from theatre_ag import Actor, AbstractClock, workflow


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

        class ExampleWorkflow(object):

            @workflow(1)
            def task_a(self):
                self.task_b()

            @workflow(1)
            def task_b(self):
                self.idle()

        class ExampleActor(ExampleWorkflow, Actor):

            def __init__(self, *args):
                Actor.__init__(self, *args)

        self.actor = ExampleActor("alice", self.clock)

        self.clock.current_tick = 0
        self.actor.add_to_task_queue(self.actor.task_a, [])
        self.clock.current_tick = 1
        self.actor.start()
        self.actor.shutdown()

        self.assertEquals(True, True)

