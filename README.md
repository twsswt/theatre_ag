
# Theatre_Ag: The Software Agent Theatre

A framework for multi-agent simulations, with a particular focus on modelling socio-technical systems, implemented in
Python.

# Contributors

Tim Storer<br/>
School of Computing Science, University of Glasgow.<br/>
GitHub ID: twsswt<br>
Email: [timothy.storer@glagow.ac.uk](mailto:timothy.storer@glagow.ac.uk)

# Overview

## Terminology

Theatre_Ag follows a theatrical metaphor for its API and Architecture.  Core concepts in Theatre_Ag are:

 * **Clock** All activity in a Theatre_Ag simulation is executed with respect to a clock object that issues clock ticks
   up to a specified limit.

 * **Actor** A software agent with it's own thread of control.  Actor execution of activity is regulated by the ticks of
   clock.

 * **Setting** The problem domain 'physics' of the simulation environment.  Actors manipulate the setting when
   they execute workflows.

 * **Workflow** Task specifications implemented as Plain Old Python Classes.  Workflows describe the sequence of work
   items
   and decisions taken by actors when the workflow is executed and any state that is maintained during execution,
   allowing actors to influence the shared environment of a problem domain.
   Workflows can also be annotated with the costs of performing individual work items.

 * **Task** An instantiation of a workflow, comprising task meta data and an instance of workflow.  Individual tasks can
   be stateful and are permitted

 * **Cast** A collection of actors who will collaborate in a Theatre_Ag simulation.

 * **Episode** The specification of a cast of actors, and initial starting conditions (directions) that the cast will
   improvise from.

## Timing Model

The timing model in Theatre_Ag was designed with the simulation of socio-technical systems in mind. The timing model is
designed to represent the observation of time with respect to the
precision of a clock's tick.  The unit of a clock tick is domain specific, so could represent seconds, weeks or years.
All actors synchronize the execution of their tasks on the tick of a clock in the simulation.

The clock synchronization design is similar to turn based synchronisation models. It can be summarised as

    "explicitly inter-tick strictly deterministic and intra-tick non-deterministic."

I don't know if there is a more formal term for this. In practice, this means that if an activity
can be specified to endure for an exact number of ticks for any number of concurrently executing activities.  If, for
example, activity *a* of duration 3 is initiated at time 1, and activity *b* of duration 1 is initiated at time 2,
then  activity *b* will finish at time 3 and activity *a* will finish at time *4.  However, if two activities are
 initiated or terminate at the same time, then the ordering of the initiation or
termination (and any consequent effect on the environment) is non-deterministic.  For example if activity *a* described
above only takes duration 2 then both activities will end at time 3 and the ordering of the termination is not
controlled by Theatre_Ag.  This contrasts with other turn based timing models that are strictly deterministic because
the order of agent

# Tutorial

## Creating the Cast

## Creating an Episode

## Directing the Cast with Workflows

A workflow is represented as a plain old Python class, comprising attributes (which can store execution state) and
methods.  For example, the following class is a simple workflow for making a cup of coffee.

    class MakeCupOfTea(object):
        is_workflow = True

## Playing an Episode and Gathering Results
