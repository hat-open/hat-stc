import typing


EventName: typing.TypeAlias = str
"""Event name"""

StateName: typing.TypeAlias = str
"""State name"""

ActionName: typing.TypeAlias = str
"""Action name"""

ConditionName: typing.TypeAlias = str
"""Condition name"""


class Event(typing.NamedTuple):
    """Event instance"""
    name: EventName
    """Event name"""
    payload: typing.Any = None
    """Optional payload"""


class Transition(typing.NamedTuple):
    """Transition definition"""
    event: EventName
    """Event identifier. Occurrence of event with this exact identifier can
    trigger state transition."""
    target: StateName | None
    """Destination state identifier. If destination state is not defined,
    local transition is assumed - state is not changed and transition
    actions are triggered."""
    actions: list[ActionName] = []
    """Actions executed on transition."""
    conditions: list[ConditionName] = []
    """List of conditions. Transition is triggered only if all provided
    conditions are met."""
    internal: bool = False
    """Internal transition modifier. Determines whether the source state is
    exited in transitions whose target state is a descendant of the source
    state."""


class State(typing.NamedTuple):
    """State definition"""
    name: StateName
    """Unique state identifier."""
    children: typing.List['State'] = []
    """Optional child states. If state has children, first child is
    considered as its initial state."""
    transitions: list[Transition] = []
    """Possible transitions to other states."""
    entries: list[ActionName] = []
    """Actions executed when state is entered."""
    exits: list[ActionName] = []
    """Actions executed when state is exited."""
    final: bool = False
    """Is state final."""
