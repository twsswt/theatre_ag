import inspect

from Queue import Queue, Empty
from threading import Event, RLock, Thread


def default_cost(cost=0):
    def workflow_decorator(func):
        func.default_cost = cost
        return func
    return workflow_decorator


class AllocatedTask(object):

    def __init__(self, workflow, entry_point, args):
        self.workflow = workflow
        self.entry_point = entry_point
        self.args = args

        self.completion_information = None

    def __repr__(self):
        return "t_(%s, %s)" % (str(self.entry_point.func_name), str(self.args))

    @property
    def completed(self):
        return self.completion_information is not None


class CompletedTask(object):

    def __init__(self, func, parent, start_tick):
        self.parent = parent
        self.sub_tasks = list()

        self.func = func
        self.start_tick = start_tick
        self.finish_tick = -1

    def append_sub_task(self, sub_task):
        self.sub_tasks.append(sub_task)
        pass

    def __str__(self):
        return "%s(%d->%d)" % (self.func.func_name, self.start_tick, self.finish_tick)

    def __repr__(self):
        return self.__str__()


class Workflow(object):

    def __init__(self, actor, logging=True):
        self.logging = logging
        self.actor = actor

    def __getattribute__(self, item):

        attribute = object.__getattribute__(self, item)

        if inspect.ismethod(attribute):

            def sync_wrap(*args, **kwargs):
                self.actor.busy.acquire()
                if self.logging:
                    self.actor.log_task_initiation(attribute)

                # TODO Pass function name and indicative cost to a cost calculation function.
                if hasattr(attribute, 'default_cost'):
                    self.actor.incur_delay(attribute.default_cost)

                self.actor.wait_for_turn()

                result = attribute.im_func(self, *args, **kwargs)

                if self.logging:
                    self.actor.log_task_completion()

                self.actor.busy.release()
                return result

            sync_wrap.func_name = attribute.im_func.func_name

            return sync_wrap
        else:
            return attribute


class Idling(Workflow):
    """
    A workflow that allows an actor to waste a turn.
    """

    @default_cost(1)
    def idle(self): pass

    def idle_until(self, allocated_task):
        while not allocated_task.completed:
            self.idle()


class Actor(object):
    """
    Models the work behaviour of a self-directing entity.
    """

    def __init__(self, logical_name, clock):
        self.logical_name = logical_name
        self.clock = clock

        self.tick_received = Event()
        self.tick_received.clear()
        self.waiting_for_tick = Event()
        self.waiting_for_tick.clear()

        self.busy = RLock()
        self.wait_for_directions = True
        self.thread = Thread(target=self.perform)

        self.clock.add_tick_listener(self)

        self.completed_tasks = []
        self.current_task = None

        self.task_queue = Queue()

        self.idling = Idling(self, logging=False)
        self.idling.actor = self

        self.next_turn = 0

    def allocate_task(self, workflow, entry_point, args=list()):
        workflow.actor = self
        allocated_task = AllocatedTask(workflow, entry_point, args)
        self.task_queue.put(allocated_task)
        return allocated_task

    def log_task_initiation(self, attribute):
        new_task = CompletedTask(attribute, self.current_task, self.clock.current_tick)

        if self.current_task is None:
            self.completed_tasks.append(new_task)
        else:
            self.current_task.append_sub_task(new_task)

        self.current_task = new_task

    def log_task_completion(self):
        self.current_task.finish_tick = self.clock.current_tick
        self.current_task = self.current_task.parent

    @property
    def last_completed_task(self):
        index = len(self.completed_tasks)-1
        if index < 0:
            return None
        else:
            return self.completed_tasks[index]

    def perform(self):
        """
        Repeatedly polls the actor's asynchronous work queue until the actor is shutdown.  On shutdown, all remaining
        tasks are processed before termination.
        """
        while self.wait_for_directions or not self.task_queue.empty():
            try:
                task = self.task_queue.get(block=False)
                print task
                if task is not None:
                    task.entry_point(*task.args)
                    task.completion_information = self.last_completed_task
            except Empty:
                self.idling.idle()

        # Ensure that clock can proceed for other listeners.
        self.clock.remove_tick_listener(self)
        self.waiting_for_tick.set()

    def start(self):
        self.thread.start()

    def shutdown(self):
        self.wait_for_directions = False
        self.thread.join()

    def incur_delay(self, delay):
        self.next_turn = max(self.next_turn, self.clock.current_tick)
        self.next_turn += delay

    def wait_for_turn(self):
        while self.clock.current_tick < self.next_turn:
            self.waiting_for_tick.set()
            self.tick_received.wait()
            self.tick_received.clear()

    def notify_new_tick(self):
        self.tick_received.set()
        self.waiting_for_tick.clear()

    def __str__(self):
        return "a_%s" % self.logical_name

    def __repr__(self):
        return self.__str__()


class Team(object):
    """
    A collection of actors who synchronize their actions on a single clock.
    """

    def __init__(self, clock):
        self.clock = clock

        self.team_members = list()

    def add_member(self, logical_name):
        actor = Actor(logical_name, self.clock)
        self.team_members.append(actor)
        return actor

    def perform(self):

        self.allocate_tasks()

        for actor in self.team_members:
            actor.start()

        for actor in self.team_members:
            actor.shutdown()
