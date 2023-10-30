import collections
import io

import pytest

from hat import stc


@pytest.mark.parametrize("scxml, states", [
    (r"""<?xml version="1.0" encoding="UTF-8"?>
        <scxml xmlns="http://www.w3.org/2005/07/scxml" version="1.0">
        </scxml>""",  # NOQA
     []),

    (r"""<?xml version="1.0" encoding="UTF-8"?>
        <scxml xmlns="http://www.w3.org/2005/07/scxml" initial="s1" version="1.0">
        <state id="s1"/>
        </scxml>""",  # NOQA
     [stc.State('s1')]),

    (r"""<?xml version="1.0" encoding="UTF-8"?>
        <scxml xmlns="http://www.w3.org/2005/07/scxml" initial="s2" version="1.0">
        <state id="s1"/>
        <state id="s2"/>
        <state id="s3"/>
        </scxml>""",  # NOQA
     [stc.State('s2'),
      stc.State('s1'),
      stc.State('s3')]),

    (r"""<?xml version="1.0" encoding="UTF-8"?>
        <scxml xmlns="http://www.w3.org/2005/07/scxml" initial="s1" version="1.0">
        <state id="s1">
            <transition event="e1" target="s2"/>
            <transition event="e2" target="s1">a1</transition>
        </state>
        <state id="s2">
            <transition event="e3" target="s2" type="internal"/>
        </state>
        </scxml>""",  # NOQA
     [stc.State('s1',
                transitions=[stc.Transition('e1', 's2'),
                             stc.Transition('e2', 's1', actions=['a1'])]),
      stc.State('s2',
                transitions=[stc.Transition('e3', 's2', internal=True)])]),

    (r"""<?xml version="1.0" encoding="UTF-8"?>
        <scxml xmlns="http://www.w3.org/2005/07/scxml" initial="s1" version="1.0">
        <state id="s1" initial="s2">
            <onentry>a1</onentry>
            <state id="s2">
                <onexit>a2</onexit>
            </state>
        </state>
        <state id="s3">
            <onentry>a3</onentry>
            <onexit>a4</onexit>
        </state>
        </scxml>""",  # NOQA
     [stc.State('s1',
                entries=['a1'],
                children=[stc.State('s2', exits=['a2'])]),
      stc.State('s3',
                entries=['a3'],
                exits=['a4'])]),

    (r"""<?xml version="1.0" encoding="UTF-8"?>
        <scxml xmlns="http://www.w3.org/2005/07/scxml" initial="s1" version="1.0">
        <state id="s1">
            <transition event="e1"/>
            <transition event="e2" cond="c1"/>
            <transition event="e2" cond="c2 c3"/>
        </state>
        </scxml>""",  # NOQA
     [stc.State('s1',
                transitions=[stc.Transition('e1', None),
                             stc.Transition('e2', None,
                                            conditions=['c1']),
                             stc.Transition('e2', None,
                                            conditions=['c2', 'c3'])])]),

])
def test_parse_scxml(scxml, states):
    result = stc.parse_scxml(io.StringIO(scxml))
    assert result == states


def test_empty():
    machine = stc.Statechart([], {})
    assert machine.state is None
    assert machine.finished


def test_single_state():
    queue = collections.deque()
    states = [stc.State('s1',
                        transitions=[
                            stc.Transition('e1', 's1', ['transit']),
                            stc.Transition('e2', 's1', ['transit'], [], True)],
                        entries=['enter'],
                        exits=['exit'])]
    actions = {'enter': lambda _, e: queue.append(('enter', e)),
               'exit': lambda _, e: queue.append(('exit', e)),
               'transit': lambda _, e: queue.append(('transit', e))}
    machine = stc.Statechart(states, actions)
    assert not machine.finished
    assert machine.state == 's1'

    a, e = queue.popleft()
    assert a == 'enter'
    assert e is None

    assert not queue

    event = stc.Event('e1', None)
    machine.step(event)

    a, e = queue.popleft()
    assert (a, e) == ('exit', event)
    a, e = queue.popleft()
    assert (a, e) == ('transit', event)
    a, e = queue.popleft()
    assert (a, e) == ('enter', event)
    assert machine.state == 's1'

    assert not queue

    event = stc.Event('e2', 123)
    machine.step(event)

    a, e = queue.popleft()
    assert (a, e) == ('transit', event)
    assert machine.state == 's1'

    assert not queue

    event = stc.Event('e3', None)
    machine.step(event)

    assert not queue
    assert machine.state == 's1'


def test_nested_states():
    queue = collections.deque()
    states = [stc.State(
        's1',
        children=[
            stc.State(
                's2',
                children=[
                    stc.State(
                        's3',
                        transitions=[stc.Transition('e1', 's4', ['transit1'])],
                        entries=['enter_s3'],
                        exits=['exit_s3']),
                    stc.State(
                        's4',
                        entries=['enter_s4'],
                        exits=['exit_s4'])],
                entries=['enter_s2'],
                exits=['exit_s2'])],
        transitions=[stc.Transition('e2', 's2', ['transit2'])],
        entries=['enter_s1'],
        exits=['exit_s1'])]
    actions = {'enter_s1': lambda _, e: queue.append(('enter_s1', e)),
               'exit_s1': lambda _, e: queue.append(('exit_s1', e)),
               'enter_s2': lambda _, e: queue.append(('enter_s2', e)),
               'exit_s2': lambda _, e: queue.append(('exit_s2', e)),
               'enter_s3': lambda _, e: queue.append(('enter_s3', e)),
               'exit_s3': lambda _, e: queue.append(('exit_s3', e)),
               'enter_s4': lambda _, e: queue.append(('enter_s4', e)),
               'exit_s4': lambda _, e: queue.append(('exit_s4', e)),
               'transit1': lambda _, e: queue.append(('transit1', e)),
               'transit2': lambda _, e: queue.append(('transit2', e))}
    machine = stc.Statechart(states, actions)

    a, e = queue.popleft()
    assert (a, e) == ('enter_s1', None)
    a, e = queue.popleft()
    assert (a, e) == ('enter_s2', None)
    a, e = queue.popleft()
    assert (a, e) == ('enter_s3', None)
    assert machine.state == 's3'

    assert not queue

    event = stc.Event('e1', 123)
    machine.step(event)

    a, e = queue.popleft()
    assert (a, e) == ('exit_s3', event)
    a, e = queue.popleft()
    assert (a, e) == ('transit1', event)
    a, e = queue.popleft()
    assert (a, e) == ('enter_s4', event)
    assert machine.state == 's4'

    assert not queue

    event = stc.Event('e2', 123)
    machine.step(event)

    a, e = queue.popleft()
    assert (a, e) == ('exit_s4', event)
    a, e = queue.popleft()
    assert (a, e) == ('exit_s2', event)
    a, e = queue.popleft()
    assert (a, e) == ('exit_s1', event)
    a, e = queue.popleft()
    assert (a, e) == ('transit2', event)
    a, e = queue.popleft()
    assert (a, e) == ('enter_s1', event)
    a, e = queue.popleft()
    assert (a, e) == ('enter_s2', event)
    a, e = queue.popleft()
    assert (a, e) == ('enter_s3', event)
    assert machine.state == 's3'

    assert not queue


def test_conditions():
    queue = collections.deque()
    states = [stc.State(
        's1',
        transitions=[
            stc.Transition('e', 's1', conditions=['c1'], actions=['a1']),
            stc.Transition('e', 's1', conditions=['c2'], actions=['a2'])])]
    conditions = {'c1': lambda _, e: e.payload == 1,
                  'c2': lambda _, e: e.payload == 2}
    actions = {'a1': lambda _, e: queue.append('a1'),
               'a2': lambda _, e: queue.append('a2')}

    machine = stc.Statechart(states, actions, conditions)

    assert not queue

    event = stc.Event('e', 1)
    machine.step(event)

    a = queue.popleft()
    assert a == 'a1'

    assert not queue

    event = stc.Event('e', 2)
    machine.step(event)

    a = queue.popleft()
    assert a == 'a2'

    assert not queue

    event = stc.Event('e', 3)
    machine.step(event)

    assert not queue


def test_local_transitions():
    queue = collections.deque()
    states = [stc.State(
        's1',
        entries=['enter'],
        transitions=[
            stc.Transition('e1', 's1', actions=['a1']),
            stc.Transition('e2', None, actions=['a2'])])]
    actions = {'enter': lambda _, e: queue.append('enter'),
               'a1': lambda _, e: queue.append('a1'),
               'a2': lambda _, e: queue.append('a2')}

    machine = stc.Statechart(states, actions)

    a = queue.popleft()
    assert a == 'enter'

    assert not queue

    event = stc.Event('e1')
    machine.step(event)

    a = queue.popleft()
    assert a == 'a1'
    a = queue.popleft()
    assert a == 'enter'

    assert not queue

    event = stc.Event('e2')
    machine.step(event)

    a = queue.popleft()
    assert a == 'a2'

    assert not queue
