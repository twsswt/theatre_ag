from threading import Thread

from unittest import TestCase

from theatre_ag import Actor, Idling, SynchronizingClock, Workflow, default_cost


class ActorTestCase(TestCase):

    def setUp(self):

        self.clock = SynchronizingClock(max_ticks=4)

    def test_idle(self):

        actor_1 = Actor("alice", self.clock)

        idling = Idling(actor_1, logging=True)
        actor_1.allocate_task(idling, idling.idle, [])
        actor_1.start()
        self.clock.start()
        actor_1.shutdown()

        self.assertEquals(1, actor_1.last_completed_task.finish_tick)

    def test_nested_task(self):

        actor_1 = Actor("alice", self.clock)

        class ExampleWorkflow(Workflow):

            def __init__(self, idle):
                super(ExampleWorkflow, self).__init__(self)
                self.idle = idle

            @default_cost(1)
            def task_a(self):
                self.task_b()

            @default_cost(1)
            def task_b(self):
                self.idle.idle()

        workflow = ExampleWorkflow(Idling(actor_1))

        actor_1.allocate_task(workflow, workflow.task_a, [])

        actor_1.start()
        self.clock.start()
        actor_1.shutdown()

        self.assertEquals(actor_1.last_completed_task.finish_tick, 3)

    def test_multiple_actors(self):

        actor_1 = Actor("alice", self.clock)
        actor_2 = Actor("bob", self.clock)

        idle_1 = Idling(actor_1)
        actor_1.allocate_task(idle_1, idle_1.idle, [])
        idle_2 = Idling(actor_2)
        actor_2.allocate_task(idle_2, idle_2.idle, [])

        actor_1.start()
        actor_2.start()
        self.clock.start()
        actor_1.shutdown()
        actor_2.shutdown()

        self.assertEquals(actor_1.last_completed_task.finish_tick, 1)
        self.assertEquals(actor_2.last_completed_task.finish_tick, 1)



