from unittest import TestCase

from theatre_ag import TaskQueueActor, Idling, SynchronizingClock, default_cost


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

    @default_cost(1)
    def task_c(self):
        raise Exception('An expected exception.')


class ActorTestCase(TestCase):

    def setUp(self):
        self.clock = SynchronizingClock(max_ticks=4)
        self.actor = TaskQueueActor(0, self.clock)
        self.idling = Idling()
        self.example_workflow = ExampleWorkflow(self.idling)

    def run_clock(self):
        self.actor.start()
        self.clock.start()
        self.clock.wait_for_last_tick()

    def test_explicit_idle(self):
        self.actor.allocate_task(self.idling.idle, self.idling)
        self.actor.initiate_shutdown()

        self.run_clock()

        self.assertEqual(1, self.actor.last_task.finish_tick)

    def test_idling_when_nothing_to_do(self):

        self.run_clock()

        self.assertEqual(0, len(self.actor.task_history))

    def test_finish_tasks_before_shutdown(self):

        self.actor.allocate_task(self.idling.idle, self.idling)
        self.actor.allocate_task(self.idling.idle, self.idling)
        self.actor.allocate_task(self.idling.idle, self.idling)
        self.actor.initiate_shutdown()

        self.run_clock()

        self.assertEqual(3, self.actor.last_task.finish_tick)

    def test_idling_when_nothing_to_do_after_completed_task(self):

        self.actor.allocate_task(self.idling.idle, self.idling)

        self.run_clock()

        self.assertEqual(1, self.actor.last_task.finish_tick)

    def test_nested_task(self):

        self.actor.allocate_task(self.example_workflow.task_a, self.example_workflow)
        self.actor.initiate_shutdown()

        self.run_clock()

        self.assertEqual(self.actor.last_task.finish_tick, 3)

    def test_encounter_exception_shutdown_cleanly(self):

        self.actor.allocate_task(self.example_workflow.task_c, self.example_workflow)

        self.run_clock()

        self.assertEqual('task_c()[0->1]', str(self.actor.last_task))

    def test_insufficient_time_shutdown_cleanly(self):
        """
        Demonstrate that actors can shutdown cleanly if their allocated tasks proceed beyond the maximum clock time.
        """
        self.actor.allocate_task(self.idling.idle_for, self.idling, [5])

        self.run_clock()
        self.actor.shutdown()

        self.assertEqual(5, len(self.actor._task_history[0].sub_tasks))
        self.assertEqual(None, self.actor._task_history[0].finish_tick)

    def test_stateless_task_allocation(self):

        @default_cost(1)
        def example_task(): pass

        self.actor.allocate_task(example_task)

        self.run_clock()

        self.assertEqual('example_task()[0->1]', str(self.actor.last_task))

    def test_task_with_implicit_state_allocation(self):

        self.actor.allocate_task(self.example_workflow.task_b)

        self.run_clock()

        self.assertEqual('task_b()[0->2]', str(self.actor.last_task))

