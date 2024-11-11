from collections.abc import Iterable

from hat.stc.common import State


def create_dot_graph(states: Iterable[State]) -> str:
    """Create DOT representation of statechart"""
    state_name_ids = {}
    id_prefix = 'state'
    states_dot = '\n'.join(
        _create_dot_graph_states(states, state_name_ids, id_prefix))
    transitions_dot = '\n'.join(
        _create_dot_graph_transitions(states, state_name_ids, id_prefix))
    return _dot_graph.format(states=states_dot,
                             transitions=transitions_dot)


def _create_dot_graph_states(states, state_name_ids, id_prefix):
    if not states:
        return
    yield _dot_graph_initial.format(id=f'{id_prefix}_initial')
    for i, state in enumerate(states):
        state_id = f'{id_prefix}_{i}'
        state_name_ids[state.name] = state_id
        actions = '\n'.join(_create_dot_graph_state_actions(state))
        separator = _dot_graph_separator if actions else ''
        children = '\n'.join(
            _create_dot_graph_states(state.children, state_name_ids, state_id))
        yield _dot_graph_state.format(id=state_id,
                                      name=state.name,
                                      separator=separator,
                                      actions=actions,
                                      children=children)


def _create_dot_graph_state_actions(state):
    for name in state.entries:
        yield _dot_graph_state_action.format(type='entry', name=name)
    for name in state.entries:
        yield _dot_graph_state_action.format(type='exit', name=name)


def _create_dot_graph_transitions(states, state_name_ids, id_prefix):
    if not states:
        return
    yield _dot_graph_transition.format(src_id=f'{id_prefix}_initial',
                                       dst_id=f'{id_prefix}_0',
                                       label='""',
                                       lhead=f'cluster_{id_prefix}_0',
                                       ltail='')
    for state in states:
        src_id = state_name_ids[state.name]
        for transition in state.transitions:
            dst_id = (state_name_ids[transition.target] if transition.target
                      else src_id)
            label = _create_dot_graph_transition_label(transition)
            lhead = f'cluster_{dst_id}'
            ltail = f'cluster_{src_id}'
            if lhead == ltail:
                lhead, ltail = '', ''
            elif ltail.startswith(lhead):
                lhead = ''
            elif lhead.startswith(ltail):
                ltail = ''
            yield _dot_graph_transition.format(src_id=src_id,
                                               dst_id=dst_id,
                                               label=label,
                                               lhead=lhead,
                                               ltail=ltail)
        yield from _create_dot_graph_transitions(state.children,
                                                 state_name_ids, src_id)


def _create_dot_graph_transition_label(transition):
    separator = (_dot_graph_separator
                 if transition.actions or transition.conditions
                 else '')
    actions = '\n'.join(_dot_graph_transition_action.format(name=name)
                        for name in transition.actions)
    condition = (f" [{' '.join(transition.conditions)}]"
                 if transition.conditions else "")
    internal = ' (internal)' if transition.internal else ''
    local = ' (local)' if transition.target is None else ''
    return _dot_graph_transition_label.format(event=transition.event,
                                              condition=condition,
                                              internal=internal,
                                              local=local,
                                              separator=separator,
                                              actions=actions)


_dot_graph = r"""digraph "stc" {{
    fontname = Helvetica
    fontsize = 12
    penwidth = 2.0
    splines = true
    ordering = out
    compound = true
    overlap = scale
    nodesep = 0.3
    ranksep = 0.1
    node [
        shape = plaintext
        style = filled
        fillcolor = transparent
        fontname = Helvetica
        fontsize = 12
        penwidth = 2.0
    ]
    edge [
        fontname = Helvetica
        fontsize = 12
    ]
    {states}
    {transitions}
}}
"""

_dot_graph_initial = r"""{id} [
    shape = circle
    style = filled
    fillcolor = black
    fixedsize = true
    height = 0.15
    label = ""
]"""

_dot_graph_state = r"""subgraph "cluster_{id}" {{
    label = <
        <table cellborder="0" border="0">
            <tr><td>{name}</td></tr>
            {separator}
            {actions}
        </table>
    >
    style = rounded
    penwidth = 2.0
    {children}
    {id} [
        shape=point
        style=invis
        margin=0
        width=0
        height=0
        fixedsize=true
    ]
}}"""

_dot_graph_separator = "<hr/>"

_dot_graph_state_action = r"""<tr><td align="left">{type}/ {name}</td></tr>"""

_dot_graph_transition = r"""{src_id} -> {dst_id} [
    label = {label}
    lhead = "{lhead}"
    ltail = "{ltail}"
]"""

_dot_graph_transition_label = r"""<
<table cellborder="0" border="0">
    <tr><td>{event}{condition}{internal}{local}</td></tr>
    {separator}
    {actions}
</table>
>"""

_dot_graph_transition_action = r"""<tr><td>{name}</td></tr>"""
