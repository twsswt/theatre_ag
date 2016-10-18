from Queue import Queue
from threading import Lock, Thread


class ActorExhaustedException(Exception):
    def __init__(self, developer):
        self.developer = developer


class Task(object):
    def __init__(self, cost, func, args):
        self.cost = cost
        self.func = func
        self.args = args


class Actor(object):
    """
    Models the work behaviour of a self-directing entity.
    """

    def __init__(self, logical_name, clock, person_time=0):
        self.logical_name = logical_name
        self.clock = clock

        self.busy = Lock()
        self.wait_for_directions = True
        self.thread = Thread(target=self.perform)

        self.completed_tasks = []
        self.task_queue = Queue()

        self.person_time = person_time

    @property
    def get_workload(self):
        return sum(map(lambda t: t.cost, self.tasks))

    def add_task_to_work_queue(self, cost=0, func=None, args=None):
        self.task_queue.put(Task(cost, func, args))

    def perform(self):
        """
        Repeatedly polls the actor's
        """
        while self.wait_for_directions or not self.task_queue.empty():
            self.perform_task()

    def perform_task(self):
        """
        Perform one task retrieved from the actor's work queue.  This method will block if the agent is already
        performing a task.
        """
        self.busy.acquire()
        task = self.task_queue.get()

        if self.person_time - task.cost <= 0:
            raise ActorExhaustedException(self)
        else:
            start_tick = self.clock.current_tick
            self.clock.set_alarm(start_tick + task.cost)
            self.person_time -= task.cost
            if task.func is not None:
                task.func(*task.args)
                self.completed_tasks.append([task.func, task.args])

        self.busy.release()

    def start(self):
        self.thread.start()

    def shutdown(self):
        self.wait_for_directions = False
        self.thread.join()

    def idle(self):
        self.add_task_to_work_queue(1)
