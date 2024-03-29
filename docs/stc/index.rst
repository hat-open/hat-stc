`hat.stc` - Python statechart library
=====================================

This library provides basic implementation of
`hierarchical state machine <https://en.wikipedia.org/wiki/UML_state_machine>`_
engine. Statechart definition can be provided as structures defined by API or
by `SCXML definition <https://www.w3.org/TR/scxml/>`_. Additionally,
`Graphviz <https://graphviz.org/>`_ DOT graph can be generated based on state
definition together with Sphinx extension `hat.sphinx.scxml`.

Notable differences between `hat.stc` and SCXML standard:

    * initial child state (in `scxml` and `state` tag) should be defined
      only by setting parent's `initial` attribute

    * transitions without associated event name are not supported

    * parallel substates are not supported

    * history pseudo-state is not supported

    * data model is not supported

    * external communications is not supported

    * all actions and conditions are identified by name - arbitrary expressions
      or executable contents are not supported

    * transition event identifiers are used as exact event names without
      support for substring segmentation matching


Tutorial
--------

Hierarchical state machines (also known as statecharts) are abstractions
used as organization/implementation basis for algorithms that execute
continuous state changes. Interaction between "outside world" and statecharts
is usually represented with sequence of events that are directly responsible
for state changes.

In this tutorial, we will gradually introduce statechart concepts and
`hat.stc` functions/structures which will help implement those concepts.
All examples are available as part of `git repository
<https://github.com/hat-open/hat-core/tree/master/docs/libraries/stc>`_ .


Statechart definition
'''''''''''''''''''''

As an example of trivial state machine, let us borrow simple example from
`Wikipedia <https://en.wikipedia.org/wiki/File:Finite_state_machine_example_with_comments.svg>`_:

.. drawio-image:: tutorial.drawio
   :page-index: 0
   :align: center

This diagram models simple door with only two states - `opened` and `closed`.
`Opened` is initial state which can transition to `closed` state once `close`
event occurs. Similarly, once in `closed` state, door can change to `opened`
state if `open` event occurs. Both states have associated entry action (named
`printState`) which is triggered each time state is entered.

The same statechart can be described with following SCXML definition:

.. literalinclude:: door_01.scxml
    :language: xml
    :caption: :download:`door_01.scxml <door_01.scxml>`

`hat.stc` library provides function ``hat.stc.parse_scxml`` which can be used
for parsing SCXML definitions into state definitions usable by
``hat.stc.Statechart``. Equivalent definition of this SCXML represented by
``hat.stc.State`` definitions is::

    [State(name='opened',
           transitions=[Transition(event='close', target='closed')],
           entries=['printState']),
     State(name='closed',
           transitions=[Transition(event='open', target='opened')],
           entries=['printState'])]

Both SCXML and `hat.stc.State` based definitions represent identical statechart
definition and it is up to user to chose more appropriate notation for
statechart definitions. In the rest of this tutorial, we will be using
SCXML definitions.


Creating statechart instance
''''''''''''''''''''''''''''

Once we have prepared statechart definition (e.g. ``door_01.scxml``), we can
create execution environment with new statechart instance:

.. literalinclude:: tutorial_01.py
    :language: python
    :caption: :download:`tutorial_01.py <tutorial_01.py>`

During instance initialization, together with state definitions, we provide
action bindings. Action bindings is dictionary which contains all action
names, used in state definitions, associated with regular functions
providing action implementation. In our case, definition contains action
``printState`` (same action is used as entry action for both `opened` and
`closed` state) which is associated with ``act_print_state`` function - simple
function that prints current state of our statechart instance.

By keeping state definition separate from associated actions and statechart
instances, single list of state definitions can be used as blueprint for
creating arbitrary number of mutually independent instances.


Running statechart
''''''''''''''''''

Execution of statechart logic is controlled `hat.stc.Statechart.step` method.

During initialization, statechart will transition to initial state.

If `hat.stc.Statechart.step` method is used for executing statechart logic,
user is responsible for repetitive calling of `step` method which processes
one event at the time.

.. literalinclude:: tutorial_02.py
    :language: python
    :caption: :download:`tutorial_02.py - snippet <tutorial_02.py>`
    :lines: 12-18

By executing this example, following output can be expected::

    current state: opened
    registering close event
    current state: closed
    registering open event
    current state: opened


Representing statechart as python class
'''''''''''''''''''''''''''''''''''''''

To provide clean interface, we can encapsulate our derived statechart
functionality as single class:

.. literalinclude:: tutorial_03.py
    :language: python
    :caption: :download:`tutorial_03.py - snippet <tutorial_03.py>`
    :lines: 3-25

In this example, we have used `hat.stc.SyncRunner` as example of simple
event queue. With `hat.stc.SyncRunner.register` method, events are added
to end of the queue which is emptied in FIFO manner.

Now we can instantiate and test our simple door:

.. literalinclude:: tutorial_03.py
    :language: python
    :caption: :download:`tutorial_03.py - snippet <tutorial_03.py>`
    :lines: 28-35

This execution produces same result as our previous example::

    current state: opened
    registering close event
    current state: closed
    registering open event
    current state: opened


Processing registered events
''''''''''''''''''''''''''''

To help our analysis of event processing, we will introduce "force" to our
operations of door closing and opening. This "force" will be represented
with number in range [`0`, `100`] where `0` represents minimal opening/closing
force and `100` represents maximal opening/closing force.

This enhancement can be represented with following changes to door methods:

.. literalinclude:: tutorial_04.py
    :language: python
    :caption: :download:`tutorial_04.py - snippet <tutorial_04.py>`
    :lines: 16-26

Now our test sequence:

.. literalinclude:: tutorial_04.py
    :language: python
    :caption: :download:`tutorial_04.py - snippet <tutorial_04.py>`
    :lines: 29-38

results in::

    force None caused transition to opened
    registering close event
    force 10 caused transition to closed
    registering open event
    force 20 caused transition to opened

Each instance of `hat.std.SyncRunner` has it's own event queue. All registered
events are added to the end of this queue. During execution of
`Door.run`, events are taken one at the time from begging of
event queue and checked for possible transitions. When transition is found,
it will cause statechart instance to change it's state and execute all
appropriate actions. If transition paired with event could not be found,
event is discarded and statechart doesn't change it's state. Once all events
from the event queue are processed, `Door.run` will finish execution.

Taking this into account, execution of:

.. literalinclude:: tutorial_04.py
    :language: python
    :caption: :download:`tutorial_04.py - snippet <tutorial_04.py>`
    :lines: 40-46

results in::

    force None caused transition to opened
    registering close event
    registering open event
    force 20 caused transition to closed
    force 50 caused transition to opened

Also, if we try to open already opened door or close already closed door,
this operations will be ignored. Therefore:

.. literalinclude:: tutorial_04.py
    :language: python
    :caption: :download:`tutorial_04.py - snippet <tutorial_04.py>`
    :lines: 48-56

results in::

    force None caused transition to opened
    registering open event
    registering close event
    registering close event
    registering open event
    force 20 caused transition to closed
    force 40 caused transition to opened


Working with timeouts
'''''''''''''''''''''

As you have probably noticed, our door model reacts to close event by
immediately closing the door and to open event by immediately opening the door.
More realistic model would include transition states (`closing` and `opening`).
Duration of door being in one of these transition states should be inversely
proportional to the amount of applied force.

.. drawio-image:: tutorial.drawio
   :page-index: 1
   :align: center

.. literalinclude:: door_02.scxml
    :language: xml
    :caption: :download:`door_02.scxml <door_02.scxml>`

To help us about state transitions, we have added additional logs which
will inform us when state is entered (``logEnter``), state is exited
(``logExit``) and transition action is triggered (``logTransition``).
In addition to this logging actions, states `closing` and `opening` have
additional action responsible for starting timer with calculated timer delay.

To implement timer behavior, we will be using asyncio `loop.call_later
<https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.call_later>`_
and `hat.stc.AsyncRunner`.

.. literalinclude:: tutorial_05.py
    :language: python
    :caption: :download:`tutorial_05.py - snippet <tutorial_05.py>`
    :lines: 4-49

Execution our simple testing sequence:

.. literalinclude:: tutorial_05.py
    :language: python
    :caption: :download:`tutorial_05.py - snippet <tutorial_05.py>`
    :lines: 52-61

will result in::

    entering state opened
    registering close event
    exiting state opened
    transitioning because of event Event(name='close', payload=30)
    entering state closing
    waiting for 0.07 seconds
    exiting state closing
    transitioning because of event Event(name='timeout', payload=None)
    entering state closed
    registering open event
    exiting state closed
    transitioning because of event Event(name='open', payload=60)
    entering state opening
    waiting for 0.04 seconds
    exiting state opening
    transitioning because of event Event(name='timeout', payload=None)
    entering state opened


Composite states
''''''''''''''''

Our previous example had one major drawback - once `opening`/`closing` state
was entered, processing of future `open`/`close` events is possible only
after timeout occurs. This can be specially problematic in cases of long
timer duration which are responsible for leaving statechart "unresponsive" for
a long time.

This problem can be tackled by adding additional transitions to
`closing`/`opening` states which will enable "operation cancellation" by
returning from originating state.

In case of more complex statechart definitions, addition of transitions for
each possible event to each state can soon become hard to maintain. Alternative
to this approach is grouping states into hierarchy.

Each hierarchical statechart can be represented by equivalent non-hierarchical
state diagram but this can result in state diagrams that are harder to reason
about. Because of this, in most cases of complex definitions, we will prefer
hierarchical approach.

Hierarchical statechart definition:

.. drawio-image:: tutorial.drawio
   :page-index: 2
   :align: center

.. literalinclude:: door_03.scxml
    :language: xml
    :caption: :download:`door_03.scxml <door_03.scxml>`

Implementation of `Door` class can remain mostly the same with addition
of `stopTimer` action:

.. literalinclude:: tutorial_06.py
    :language: python
    :caption: :download:`tutorial_06.py - snippet <tutorial_06.py>`
    :lines: 38-47

Execution of testing sequence

.. literalinclude:: tutorial_06.py
    :language: python
    :caption: :download:`tutorial_06.py - snippet <tutorial_06.py>`
    :lines: 57-67

produces following output::

    entering state open_group
    entering state opened
    registering close event
    exiting state opened
    exiting state open_group
    transitioning because of event Event(name='close', payload=30)
    entering state close_group
    entering state closing
    waiting for 0.07 seconds
    registering open event
    exiting state closing
    exiting state close_group
    transitioning because of event Event(name='open', payload=60)
    entering state open_group
    entering state opening
    waiting for 0.04 seconds
    exiting state opening
    transitioning because of event Event(name='timeout', payload=None)
    entering state opened


Advanced transitions
''''''''''''''''''''

Together with regular transitions, `hat.stc` provides support for local
transitions and internal transitions.

Local transitions can not be used to change state and do not have target state.
Therefore, only useful part of local transition is possibility to associate
action which will be executed once appropriate event occurs without any state
changes.

This functionality can be used in our door simulation to process `open` events
inside `open_group` state and `close` events in `close_group` state.

.. drawio-image:: tutorial.drawio
   :page-index: 3
   :align: center

.. literalinclude:: door_04.scxml
    :language: xml
    :caption: :download:`door_04.scxml <door_04.scxml>`

In door implementation, we should add implementation of `logInvalid` action:

.. literalinclude:: tutorial_07.py
    :language: python
    :caption: :download:`tutorial_07.py - snippet <tutorial_07.py>`
    :lines: 39-40

Execution of testing sequence

.. literalinclude:: tutorial_07.py
    :language: python
    :caption: :download:`tutorial_07.py - snippet <tutorial_07.py>`
    :lines: 61-73

produces following output::

    entering state open_group
    entering state opened
    registering open event
    invalid operation open in state opened
    registering close event
    exiting state opened
    exiting state open_group
    transitioning because of event Event(name='close', payload=20)
    entering state close_group
    entering state closing
    waiting for 0.08 seconds
    exiting state closing
    transitioning because of event Event(name='timeout', payload=None)
    entering state closed
    registering close event
    invalid operation close in state closed


Transition guards
'''''''''''''''''

Each transition can have list of conditions which have to be met for event to
cause state transition. These condition guards are convenient way of adding
additional statechart logic without adding new states.

To demonstrate usage of transition conditions, we will update behavior of
our door definition by limiting number of times successful open/close
operations can occur during single door instance lifetime. Lets say that
we can open or close door maximum N times.

.. drawio-image:: tutorial.drawio
   :page-index: 4
   :align: center

.. literalinclude:: door_05.scxml
    :language: xml
    :caption: :download:`door_05.scxml <door_05.scxml>`

Condition `isOperational` and `incCounter` action have to be added to our
implementation:

.. literalinclude:: tutorial_08.py
    :language: python
    :caption: :download:`tutorial_08.py - snippet <tutorial_08.py>`
    :lines: 8-22,57-61

Execution of testing sequence

.. literalinclude:: tutorial_08.py
    :language: python
    :caption: :download:`tutorial_08.py - snippet <tutorial_08.py>`
    :lines: 71-87

produces following output::

    entering state open_group
    entering state opened
    registering close event
    exiting state opened
    exiting state open_group
    transitioning because of event Event(name='close', payload=10)
    entering state close_group
    entering state closing
    waiting for 0.09 seconds
    exiting state closing
    transitioning because of event Event(name='timeout', payload=None)
    entering state closed
    registering open event
    exiting state closed
    exiting state close_group
    transitioning because of event Event(name='open', payload=20)
    entering state open_group
    entering state opening
    waiting for 0.08 seconds
    exiting state opening
    transitioning because of event Event(name='timeout', payload=None)
    entering state opened
    registering close event
    exiting state opened
    exiting state open_group
    transitioning because of event Event(name='close', payload=30)
    entering state close_group
    entering state closing
    waiting for 0.07 seconds
    exiting state closing
    transitioning because of event Event(name='timeout', payload=None)
    entering state closed
    registering open event


Final state
'''''''''''

In our previous example, it is obvious that once counter reaches maximum value,
door are no longer operational. Instead of limiting future operations,
we could allow one more time for user to try and operate the door. However,
since the door have reach their operational limit, it is expected that
next operation will permanently disable the door instance.

For those cases where future changes of statechart states is no longer
possible, final state can be used. Final state is state as any other with
one exception, once the statechart enters this state, following transitions
are not possible.

.. drawio-image:: tutorial.drawio
   :page-index: 5
   :align: center

.. literalinclude:: door_06.scxml
    :language: xml
    :caption: :download:`door_06.scxml <door_06.scxml>`

Modification to implementation:

.. literalinclude:: tutorial_09.py
    :language: python
    :caption: :download:`tutorial_09.py - snippet <tutorial_09.py>`
    :lines: 24-27,68-69

Execution of testing sequence

.. literalinclude:: tutorial_09.py
    :language: python
    :caption: :download:`tutorial_09.py - snippet <tutorial_09.py>`
    :lines: 79-99

produces following output::

    entering state open_group
    entering state opened
    registering close event
    exiting state opened
    exiting state open_group
    transitioning because of event Event(name='close', payload=10)
    entering state close_group
    entering state closing
    waiting for 0.09 seconds
    exiting state closing
    transitioning because of event Event(name='timeout', payload=None)
    entering state closed
    registering open event
    exiting state closed
    exiting state close_group
    transitioning because of event Event(name='open', payload=20)
    entering state open_group
    entering state opening
    waiting for 0.08 seconds
    exiting state opening
    transitioning because of event Event(name='timeout', payload=None)
    entering state opened
    registering close event
    exiting state opened
    exiting state open_group
    transitioning because of event Event(name='close', payload=30)
    entering state close_group
    entering state closing
    waiting for 0.07 seconds
    exiting state closing
    transitioning because of event Event(name='timeout', payload=None)
    entering state closed
    is finished: False
    registering open event
    exiting state closed
    exiting state close_group
    transitioning because of event Event(name='open', payload=40)
    entering state final
    is finished: True


API
---

API reference is available as part of generated documentation:

    * `Python hat.stc module <../py_api/hat/stc.html>`_
