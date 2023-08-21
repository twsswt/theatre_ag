import inspect

import threading


def default_cost(cost=0):
    def workflow_decorator(func):
        func.default_cost = cost
        return func
    return workflow_decorator


def allocate_workflow_to(workflow, logging=True):
    """
    Allocates the workflow to the specified actor for timing synchronization purposes.  The members of the workflow are
    recursively inspected.  Any member with the class attribute 'is_workflow' is also allocated to this actor if it has
    not previously been allocated to another actor.
    """
    workflow.logging = logging

    workflow_class = workflow.__class__

    if not workflow_class.__getattribute__.__name__ == '__tracked_getattribute':
        treat_as_workflow(workflow_class)

    for name, member in inspect.getmembers(workflow):
        if hasattr(member.__class__, 'is_workflow'):
            allocate_workflow_to(member, logging)


def treat_as_workflow(workflow_class):
    """
    Modifies the specified class to intercept __getattribute__ calls for task methods of a workflow, and synchronise
    their execution with an actor.  The underlying 'reference' __getattribute__ method is retained and used to access
    the underlying workflow task method for execution within the synchronization machinery.
    """

    reference_get_attr = workflow_class.__getattribute__

    def __tracked_getattribute(self, item):

        attribute = reference_get_attr(self, item)

        if hasattr(attribute, '__func__') and attribute.__func__.__name__[0:2] == '__':
            return attribute

        elif inspect.ismethod(attribute) or inspect.isfunction(attribute):
            def sync_wrap(*args, **kwargs):
                current_thread = threading.current_thread()
                if hasattr(current_thread, 'actor'):
                    actor = current_thread.actor
                    actor.busy.acquire()
                    actor.log_task_initiation(attribute, self, args)

                    # TODO Pass function name and indicative cost to a cost calculation function.

                    actor.incur_delay(attribute, self, args)
                    actor.wait_for_turn()

                    try:
                        return attribute.__func__(self, *args, **kwargs) if inspect.ismethod(attribute) \
                            else attribute(*args, **kwargs)
                    finally:
                        actor.log_task_completion()
                        actor.busy.release()
                else:
                    return attribute.__func__(self, *args, **kwargs)

            if inspect.ismethod(attribute):
                sync_wrap.__name__ = attribute.__func__.__name__
            else:
                sync_wrap.__name__ = attribute.__name__

            return sync_wrap

        else:
            return attribute

    workflow_class.__getattribute__ = __tracked_getattribute


class Idling(object):
    """
    A workflow that allows an actor to waste a turn.
    """

    is_workflow = True

    @default_cost(0)
    def idle_for(self, duration):
        for _ in range(0, duration):
            self.idle()

    @default_cost(0)
    def wait_for_tasks(self, allocated_tasks):
        for task in allocated_tasks:
            self.idle_until(task)

    @default_cost(0)
    def idle_until(self, allocated_task):
        while not allocated_task.completed:
            self.idle()

    @default_cost(1)
    def idle(self):
        pass
