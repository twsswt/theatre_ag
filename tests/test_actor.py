from unittest import TestCase

from theatre_ag import Actor, Idle, SynchronizingClock, Workflow, default_cost


class ActorTestCase(TestCase):

    def setUp(self):

        self.clock = SynchronizingClock()

        self.actor = Actor("alice", self.clock)

    def test_idle(self):
        idle = Idle(self.actor)
        self.actor.allocate_task(idle.idle, [])
        self.actor.start()
        self.clock.tick()
        self.clock.tick()
        self.actor.shutdown()

        self.assertEquals(self.actor.last_completed_task.finish_tick, 1)

    def test_nested_task(self):

        class ExampleWorkflow(Workflow):

            def __init__(self, actor, idle):
                Workflow.__init__(self, actor)
                self.idle = idle

            @default_cost(1)
            def task_a(self):
                self.task_b()

            @default_cost(1)
            def task_b(self):
                self.idle.idle()

        workflow = ExampleWorkflow(self.actor, Idle(self.actor))

        self.actor.allocate_task(workflow.task_a, [])

        self.actor.start()
        self.clock.tick()
        self.clock.tick()
        self.clock.tick()
        self.clock.tick()
        self.actor.shutdown()

        self.assertEquals(self.actor.last_completed_task.finish_tick, 3)

