from Queue import Queue, Empty
from threading import Event, RLock, Thread

from .task import AllocatedTask, CompletedTask
from .workflow import allocate_workflow_to, Idling


class OutOfTurnsException(Exception):
    pass


class Actor(object):
    """
    Models the work behaviour of a self-directing entity.  Actors can be assigned tasks described by workflows which are
    executed in synchronization with actor's clock.
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

        self.idling = Idling()
        allocate_workflow_to(self, self.idling, logging=False)

        self.next_turn = 0

    def allocate_task(self, workflow, entry_point, args=list()):

        entry_point_name = entry_point.func_name
        allocate_workflow_to(self, workflow)
        entry_point = workflow.__getattribute__(entry_point_name)

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
        Repeatedly polls the actor's asynchronous work queue until the actor is shutdown.  Tasks in the work queue are
        executed synchronously until shutdown.  On shutdown, all remaining tasks in the queue are processed before
        termination.  Task execution will halt immediately if the actor's clock runs up to it's maximum tick count.
        """
        while self.wait_for_directions or not self.task_queue.empty():
            try:
                try:
                    task = self.task_queue.get(block=False)
                    if task is not None:
                        task.entry_point(*task.args)
                        task.completion_information = self.last_completed_task
                except Empty:
                    self.idling.idle()
            except OutOfTurnsException:
                break

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
        """
        A method that blocks while the actor's clock time is less than the time of the actor's next turn.
        """
        while self.clock.current_tick < self.next_turn:
            if self.clock.will_tick_again:
                self.waiting_for_tick.set()
                self.tick_received.wait()
                self.tick_received.clear()
            else:
                raise OutOfTurnsException()

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

        for actor in self.team_members:
            actor.start()

        for actor in self.team_members:
            actor.shutdown()
