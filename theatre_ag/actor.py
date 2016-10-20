from Queue import Queue
from threading import RLock, Thread


class Task(object):

    def __init__(self, func, args):
        self.func = func
        self.args = args

    def __repr__(self):
        return "t_(%s, %d)" %(str(self.func), self.cost)


class default_cost(object):

    def __init__(self, cost):
        self.cost = cost

    def __call__(self, func):
        return func


class Actor(object):
    """
    Models the work behaviour of a self-directing entity.
    """

    def __init__(self, logical_name, clock):
        self.logical_name = logical_name
        self.clock = clock

        self.busy = RLock()
        self.wait_for_directions = True
        self.thread = Thread(target=self.perform)

        self.completed_tasks = []
        self.task_queue = Queue()

    def add_to_task_queue(self, func, args=[]):
        self.task_queue.put(Task(func, args))

    def perform(self):
        """
        Repeatedly polls the actor's asynchronous work queue.
        """
        while self.wait_for_directions or not self.task_queue.empty():
            task = self.task_queue.get(block=False)
            if task is not None:
                self.perform_task(task.func, task.args)

    def perform_task(self, task, args=[]):

        self.busy.acquire()

        if hasattr(task, 'default_cost'):
            self._incur_cost(task.default_cost)

        args.insert(0, self)

        task(*args)

        self.completed_tasks.append((task, self.clock.current_tick))

        self.busy.release()

    def start(self):
        self.thread.start()

    def shutdown(self):
        self.wait_for_directions = False
        self.thread.join()

    def _incur_cost(self, cost):
        start_tick = self.clock.current_tick
        self.clock.set_alarm(start_tick + cost)

    @default_cost(1)
    def idle(self):
        pass