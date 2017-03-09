from unittest import TestCase

from theatre_ag import Actor, Idling, SynchronizingClock, default_cost


class ActorTestCase(TestCase):

    def setUp(self):

        self.clock = SynchronizingClock(max_ticks=4)

    def test_explicit_idle(self):

        actor = Actor(0, self.clock)

        idling = Idling()
        actor.allocate_task(idling, idling.idle, [])

        actor.initiate_shutdown()

        actor.start()
        self.clock.start()
        actor.wait_for_shutdown()

        self.assertEquals(1, actor.last_task.finish_tick)

    def test_idling_when_nothing_to_do(self):

        actor = Actor(0, self.clock)
        actor.start()

        self.clock.start()
        self.clock.wait_for_last_tick()

        self.assertEquals(0, len(actor.task_history))

    def test_idling_when_nothing_to_do_after_completed_task(self):

        actor = Actor(0, self.clock)

        idling = Idling()
        actor.allocate_task(idling, idling.idle, [])

        actor.start()
        self.clock.start()

        self.clock.wait_for_last_tick()

        self.assertEquals(1, actor.last_task.finish_tick)

    def test_nested_task(self):

        actor = Actor(0, self.clock)

        class ExampleWorkflow(object):

            is_workflow = True

            def __init__(self, idling):
                self.idling = idling

            @default_cost(1)
            def task_a(self):
                self.task_b()

            @default_cost(1)
            def task_b(self):
                self.idling.idle()

        workflow = ExampleWorkflow(Idling())

        actor.allocate_task(workflow, workflow.task_a, [])

        actor.start()
        self.clock.start()
        actor.shutdown()

        self.assertEquals(actor.last_task.finish_tick, 3)

    def test_multiple_actors(self):

        actors = list()

        def add_actor_to_test(logical_name):
            _actor = Actor(logical_name, self.clock)
            idle_task = Idling()
            _actor.allocate_task(idle_task, idle_task.idle)
            _actor.initiate_shutdown()
            actors.append(_actor)
            _actor.start()

        for name in range(0, 10):
            add_actor_to_test(name)

        self.clock.start()

        for actor in actors:
            actor.wait_for_shutdown()

        for actor in actors:
            self.assertEquals('idle()[0->1]', str(actor.last_task))

    def test_encounter_exception_shutdown_cleanly(self):

        class ExampleWorkflow(object):
            is_workflow = True

            @default_cost(1)
            def task_a(self):
                raise Exception("Example exception.")

        example_task = ExampleWorkflow()
        actor = Actor(0, self.clock)
        actor.allocate_task(example_task, example_task.task_a)
        actor.start()
        self.clock.start()
        self.clock.wait_for_last_tick()

        self.assertEquals('task_a()[0->1]', str(actor.last_task))

    def test_insufficient_time_shutdown_cleanly(self):
        """
        Demonstrate that actors can shutdown cleanly if their allocated tasks proceed beyond the maximum clock time.
        """
        clock = SynchronizingClock(max_ticks=2)
        actor = Actor(0, clock)
        idling = Idling()
        actor.allocate_task(idling, idling.idle_for, [3])

        actor.start()
        clock.start()
        actor.shutdown()

        self.assertEquals(3, len(actor._task_history[0].sub_tasks))
        self.assertEquals(None, actor._task_history[0].finish_tick)




