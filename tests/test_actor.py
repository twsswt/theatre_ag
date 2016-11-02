from threading import Thread

from unittest import TestCase

from theatre_ag import Actor, Idle, SynchronizingClock, Workflow, default_cost


class ActorTestCase(TestCase):

    def setUp(self):

        self.clock = SynchronizingClock(max_ticks=4)

        self.clock_thread = Thread(target=self.clock.tick_toc)

        self.actor_1 = Actor("alice", self.clock)
        self.actor_2 = Actor("bob", self.clock)

    def test_idle(self):
        idle = Idle(self.actor_1)
        self.actor_1.allocate_task(idle.idle, [])
        self.actor_1.start()
        self.actor_2.start()
        self.clock_thread.start()
        self.actor_1.shutdown()
        self.actor_2.shutdown()

        self.assertEquals(self.actor_1.last_completed_task.finish_tick, 1)

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

        workflow = ExampleWorkflow(self.actor_1, Idle(self.actor_1))

        self.actor_1.allocate_task(workflow.task_a, [])

        self.actor_1.start()
        self.actor_2.start()
        self.clock_thread.start()
        self.actor_1.shutdown()
        self.actor_2.shutdown()

        self.assertEquals(self.actor_1.last_completed_task.finish_tick, 3)

    def test_multiple_actors(self):
        idle_1 = Idle(self.actor_1)
        self.actor_1.allocate_task(idle_1.idle, [])
        idle_2 = Idle(self.actor_2)
        self.actor_2.allocate_task(idle_2.idle, [])

        self.actor_1.start()
        self.actor_2.start()
        self.clock_thread.start()
        self.actor_1.shutdown()
        self.actor_2.shutdown()

        self.assertEquals(self.actor_1.last_completed_task.finish_tick, 1)
        self.assertEquals(self.actor_2.last_completed_task.finish_tick, 1)



