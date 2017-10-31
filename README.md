
# Theatre_Ag: The Software Agent Theatre

A Python based environment for multi-agent simulations, with a particular focus on modelling socio-technical systems.

## Contributors

Tim Storer<br/>
School of Computing Science, University of Glasgow.<br/>
GitHub ID: twsswt<br>
Email: [timothy.storer@glagow.ac.uk](mailto:timothy.storer@glagow.ac.uk)

Tom Wallis<br/>
School of Computing Science, University of Glasgow.<br/>
GitHub ID: probablytom<br>
Email: [twallisgm@gmail.com](mailto:twallisgm@gmail.com)

## Overview

Theatre_Ag is a workflow oriented agent based simulation environment.  Theatre_Ag is designed to enable experimenters to
specify readable workflows directly as collections of related methods organised into Plain Old Python Classes that are
executed by the agents in the simulation.  All other simulation machinery (critically task duration and clock
synchronization is handled internally by the simulation environment.

## Terminology

Theatre_Ag follows a theatrical metaphor for its API and Architecture.  Core concepts in Theatre_Ag are:

 * **Clock:** All activity in a Theatre_Ag simulation is executed with respect to a clock object that issues clock ticks
   up to a specified limit.

 * **Actor:** A software agent with it's own thread of control.  Actor execution of activity is regulated by the ticks of
   clock.

 * **Scene:** The problem domain 'physics' of the simulation environment.  Actors manipulate the setting when
   they execute workflows.

 * **Workflow:** Task specifications implemented as Plain Old Python Classes.  Workflows describe the sequence of work
   items
   and decisions taken by actors when the workflow is executed and any state that is maintained during execution,
   allowing actors to influence the shared environment of a problem domain.
   Workflows can also be annotated with the costs of performing individual work items.

 * **Task:** An instantiation of a workflow, comprising task meta data and an instance of workflow.  Individual tasks can
   be stateful and are permitted

 * **Cast:** A collection of actors who will collaborate in a Theatre_Ag simulation.

 * **Episode:** The specification of a cast of actors, and initial starting conditions (directions) that the cast will
   improvise from.

## Timing Model

The timing model in Theatre_Ag was designed with the simulation of socio-technical systems in mind. The timing model is
designed to represent the observation of time with respect to the precision of a clock's tick.  The unit of a clock tick
is domain specific, so could represent seconds, weeks or years. All actors synchronize the execution of their tasks on
the tick of a clock in the simulation.

The clock synchronization design is similar to turn based synchronisation models. It can be summarised as:

> "explicitly inter-tick strictly deterministic and intra-tick non-deterministic."

I don't know if there is a more formal term for this. In practice, this means that if an activity
can be specified to endure for an exact number of ticks for any number of concurrently executing activities.  If, for
example, activity *a* of duration 3 is initiated at time 1, and activity *b* of duration 1 is initiated at time 2,
then  activity *b* will finish at time 3 and activity *a* will finish at time 4.  However, if two activities are
initiated or terminate at the same time, then the ordering of the initiation or
termination (and any consequent effect on the environment) is non-deterministic.  For example if activity *a* described
above only takes duration 2 then both activities will end at time 3 and the ordering of the termination is not
controlled by Theatre_Ag.  This contrasts with other turn based timing models that are strictly deterministic because
the order of agent execution during a turn can be pre-determined.

## Actors

The basic behaviour of actors is implemented in the <code>actor.Actor</code> class.

### Task Processing in the Perform Control Loop

Actors are implemented as a threaded process managed by the <code>perform</code> method. The perform method loops
repeatedly as long as the actor still has tasks to be performed (<code>tasks_waiting</code> is True) or the actor is
waiting for more tasks.

Perform follows the following procedure in each loop:

    Poll for a new task by calling get_next_task()
    If a new task is available then:
        Log the task initiation.
        Calculate the cost of performing the task by calling calculate_delay().
        Wait for this number of ticks on the actor's clock.

        Execute the task.
        If task execution is normal then:
            Pass return values from task invocation to handle_task_return().
        Else:
            Silently handle exception

        Log the completion of the task.

    Else:
        idle for one tick.

Tasks may raise exceptions.  In this circumstance, the task will be immediately terminated with no return value handled.
However, the actor itself will not halt and will continue to process further tasks as normal.

### Shutdown

Actors will idle indefinitely while waiting for tasks to perform. Actor shutdown can happen in three ways:

 * The <code>initiate_shutdown</code> method is invoked.  When this happens, the actor will continue to poll for more
   tasks by calling  <code>get_next_task()</code>, but will halt as soon as no tasks is returned.

 * The actor's clock reaches it's maximum tick while the actor is idling.  In this case, the actor will immediately
   halt.

 * The actor's clock reaches it's maximum tick while waiting for the cost period of a task. In this case, the actor
   will immediately halt.  The current task will be logged as incomplete in the Actor's task history.

### Configuration

The perform method behaviour can be configured in a sub-class by implementing the following three methods:

 * <code>get_next_task(self):Task</code>

   Called each time a new task is needed for invocation.  Implementing classes of Actor must override this method to
   provide a means of scheduling actor tasks.  Implementations of this method must return a <code>Task</code> object.

 * <code>handle_task_return(self, task, return_value):None</code>

   Called each time a task invocation completes.

 * <code>tasks_waiting(self):False</code>

   Called at the start of each perform loop to determine whether at least one task is available for invocation.

 * <code>calculate_delay(self, entry_point, workflow, args):int</code>

   Called immediately prior to executing a task to determine the number of ticks that must be observed before the
   entry point to a task is invoked.

The <code>TaskQueueActor</code> provides an example of how to override the default implementations of these methods.

## Tutorials and Examples

 * There is a Jupyter Notebook tutorial available [./tutorial.ipynb](./tutorial.ipynb).
