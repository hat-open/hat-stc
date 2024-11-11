"""Statechart module"""

from collections.abc import Callable, Iterable
import collections
import typing

from hat.stc.common import StateName, ActionName, ConditionName, Event, State


Action: typing.TypeAlias = Callable[['Statechart',
                                     Event | None],
                                    None]
"""Action function

Action implementation which can be executed as part of entering/exiting
state or transition execution. It is called with statechart instance and
`Event` which triggered transition. In case of initial actions, run during
transition to initial state, it is called with ``None``.

"""

Condition: typing.TypeAlias = Callable[['Statechart',
                                        Event | None],
                                       bool]
"""Condition function

Condition implementation used as transition guard. It is called with statechart
instance and `Event` which triggered transition. Return value ``True`` is
interpreted as satisfied condition.

"""


class Statechart:
    """Statechart engine

    Each instance is initialized with state definitions (first state is
    considered initial) and action and condition definitions.

    During initialization, statechart will transition to initial state.

    Statechart execution is simulated by repetitive calling of
    `Statechart.step` method which accepts event instances containing event
    name and optional event payload.

    During statechart execution, actions and conditions are called based on
    state changes and associated transitions provided during initialization.

    Condition is considered met only if result of calling condition function is
    ``True``.

    Args:
        states: all state definitions with (first state is initial)
        actions: mapping of action names to their implementation
        conditions: mapping of conditions names to their implementation

    """

    def __init__(self,
                 states: Iterable[State],
                 actions: dict[ActionName, Action],
                 conditions: dict[ConditionName, Condition] = {}):
        states = collections.deque(states)
        initial = states[0].name if states else None

        self._actions = actions
        self._conditions = conditions
        self._states = {}
        self._parents = {}
        self._stack = collections.deque()

        while states:
            state = states.pop()
            states.extend(state.children)
            self._states[state.name] = state
            self._parents.update({i.name: state.name for i in state.children})

        if initial:
            self._walk_down(initial, None)

    @property
    def state(self) -> StateName | None:
        """Current state"""
        return self._stack[-1] if self._stack else None

    @property
    def finished(self) -> bool:
        """Is statechart in final state"""
        state = self.state
        return not state or self._states[state].final

    def step(self, event: Event):
        """Process single event"""
        if self.finished:
            return

        state, transition = self._find_state_transition(self.state, event)
        if not transition:
            return

        if transition.target:
            ancestor = self._find_ancestor(state, transition.target,
                                           transition.internal)
            self._walk_up(ancestor, event)

        self._exec_actions(transition.actions, event)

        if transition.target:
            self._walk_down(transition.target, event)

    def _walk_up(self, target, event):
        while self.state != target:
            state = self._states[self.state]
            self._exec_actions(state.exits, event)
            self._stack.pop()

    def _walk_down(self, target, event):
        states = collections.deque([self._states[target]])

        while ((state := states[0]).name != self.state and
                (parent := self._parents.get(state.name))):
            states.appendleft(self._states[parent])

        while (state := states[-1]).children:
            states.append(state.children[0])

        if states[0].name == self.state:
            states.popleft()

        for state in states:
            self._stack.append(state.name)
            self._exec_actions(state.entries, event)

    def _find_state_transition(self, state, event):
        while state:
            for transition in self._states[state].transitions:
                if transition.event != event.name:
                    continue

                if not all(self._conditions[condition](self, event)
                           for condition in transition.conditions):
                    continue

                return state, transition

            state = self._parents.get(state)

        return None, None

    def _find_ancestor(self, state, sibling, internal):
        if not sibling or not state:
            return

        path = collections.deque([sibling])
        while (parent := self._parents.get(path[0])):
            path.appendleft(parent)

        ancestor = None
        for i, j in zip(self._stack, path):
            if i != j:
                break

            if i in [sibling, state]:
                if internal and i == state:
                    ancestor = i
                break

            ancestor = i

        return ancestor

    def _exec_actions(self, names, event):
        for name in names:
            action = self._actions[name]
            action(self, event)
