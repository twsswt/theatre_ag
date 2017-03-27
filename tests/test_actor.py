from unittest import TestCase

from theatre_ag import TaskQueueActor, Idling, SynchronizingClock, default_cost


class ActorTestCase(TestCase):

    def setUp(self):

        self.clock = SynchronizingClock(max_ticks=4)
        self.actor = TaskQueueActor(0, self.clock)

    def test_explicit_idle(self):

        idling = Idling()
        self.actor.allocate_task(idling, idling.idle, [])

        self.actor.initiate_shutdown()

        self.actor.start()
        self.clock.start()
        self.actor.wait_for_shutdown()

        self.assertEquals(1, self.actor.last_task.finish_tick)

    def test_idling_when_nothing_to_do(self):

        self.actor.start()

        self.clock.start()
        self.clock.wait_for_last_tick()

        self.assertEquals(0, len(self.actor.task_history))

    def test_finish_tasks_before_shutdown(self):

        idling = Idling()
        self.actor.allocate_task(idling, idling.idle, [])
        self.actor.allocate_task(idling, idling.idle, [])
        self.actor.allocate_task(idling, idling.idle, [])

        self.actor.initiate_shutdown()

        self.actor.start()
        self.clock.start()
        self.actor.wait_for_shutdown()

        self.assertEquals(3, self.actor.last_task.finish_tick)

    def test_idling_when_nothing_to_do_after_completed_task(self):

        idling = Idling()
        self.actor.allocate_task(idling, idling.idle, [])

        self.actor.start()
        self.clock.start()

        self.clock.wait_for_last_tick()

        self.assertEquals(1, self.actor.last_task.finish_tick)

    def test_nested_task(self):

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

        self.actor.allocate_task(workflow, workflow.task_a, [])

        self.actor.start()
        self.clock.start()
        self.actor.shutdown()

        self.assertEquals(self.actor.last_task.finish_tick, 3)

    def test_encounter_exception_shutdown_cleanly(self):

        class ExampleWorkflow(object):
            is_workflow = True

            @default_cost(1)
            def task_a(self):
                raise Exception("Example exception.")

        example_task = ExampleWorkflow()

        self.actor.allocate_task(example_task, example_task.task_a)
        self.actor.start()
        self.clock.start()
        self.clock.wait_for_last_tick()

        self.assertEquals('task_a()[0->1]', str(self.actor.last_task))

    def test_insufficient_time_shutdown_cleanly(self):
        """
        Demonstrate that actors can shutdown cleanly if their allocated tasks proceed beyond the maximum clock time.
        """
        idling = Idling()
        self.actor.allocate_task(idling, idling.idle_for, [5])

        self.actor.start()
        self.clock.start()
        self.actor.shutdown()

        self.assertEquals(5, len(self.actor._task_history[0].sub_tasks))
        self.assertEquals(None, self.actor._task_history[0].finish_tick)




