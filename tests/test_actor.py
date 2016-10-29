from unittest import TestCase

from theatre_ag import Actor, Idle, SynchronizingClock, workflow


class ActorTestCase(TestCase):

    def setUp(self):

        self.clock = SynchronizingClock()

        class IdlingActor(Idle, Actor):
            def __init__(self, logical_name, clock):
                Actor.__init__(self, logical_name, clock)

        self.actor = IdlingActor("alice", self.clock)

    def test_idle(self):
        self.actor.allocate_task(self.actor.idle, [])
        self.actor.start()
        self.clock.tick()
        self.actor.shutdown()

        self.assertEquals(True, True)

    def test_nested_task(self):

        class ExampleWorkflow(Idle):

            @workflow(1)
            def task_a(self):
                self.task_b()

            @workflow(2)
            def task_b(self):
                self.idle()

        class ExampleActor(ExampleWorkflow, Actor):

            def __init__(self, *args):
                Actor.__init__(self, *args)

        self.actor = ExampleActor("alice", self.clock)
        self.actor.allocate_task(self.actor.task_a, [])
        self.actor.start()
        self.clock.tick()
        self.clock.tick()
        self.clock.tick()
        self.clock.tick()
        self.actor.shutdown()

        self.assertEquals(self.actor.completed_tasks[1][1], 4)

