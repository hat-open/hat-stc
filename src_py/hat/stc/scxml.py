"""Statechart module"""

import itertools
import typing
import xml.etree.ElementTree

from hat.stc.common import State, Transition


def parse_scxml(scxml: typing.TextIO) -> list[State]:
    """Parse SCXML into list of state definitions"""
    root_el = _read_xml(scxml)
    return _parse_scxml_states(root_el)


def _parse_scxml_states(parent_el):
    states = {}
    for state_el in itertools.chain(parent_el.findall("./state"),
                                    parent_el.findall("./final")):
        state = _parse_scxml_state(state_el)
        states[state.name] = state

    if not states:
        return []

    initial = parent_el.get('initial')
    return [states[initial], *(state for name, state in states.items()
                               if name != initial)]


def _parse_scxml_state(state_el):
    return State(
        name=state_el.get('id'),
        children=_parse_scxml_states(state_el),
        transitions=[_parse_scxml_transition(i)
                     for i in state_el.findall('./transition')],
        entries=[entry_el.text
                 for entry_el in state_el.findall('./onentry')
                 if entry_el.text],
        exits=[exit_el.text
               for exit_el in state_el.findall('./onexit')
               if exit_el.text],
        final=state_el.tag == 'final')


def _parse_scxml_transition(transition_el):
    return Transition(
        event=transition_el.get('event'),
        target=transition_el.get('target'),
        actions=[i
                 for i in (transition_el.text or '').split()
                 if i],
        conditions=[i for i in (transition_el.get('cond') or '').split()
                    if i],
        internal=transition_el.get('type') == 'internal')


def _read_xml(source):
    it = xml.etree.ElementTree.iterparse(source)
    for _, el in it:
        prefix, has_namespace, postfix = el.tag.partition('}')

        if has_namespace:
            el.tag = postfix

    return it.root
