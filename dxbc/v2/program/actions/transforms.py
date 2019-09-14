from collections import Callable
from copy import copy
from typing import List, Set

from dxbc.v2.program.actions.action import Action
from dxbc.v2.values import *

ActionTransform = Callable[[List[Action]], List[Action]]


"""def add_name_prefix(vars: Set[str], prefix: str) -> ActionTransform:
    def remap_var_name(var_name: VarNameBase) -> VarNameBase:
        new_var_name = var_name
        if new_var_name.name in vars:
            new_var_name = copy(var_name)
            new_var_name.name = prefix + new_var_name.name
        return new_var_name
    def remap_value(value: Value):
        if isinstance(value, ScalarVariable):
            return ScalarVariable(remap_var_name(value.scalar_name), value.scalar_type, value.negated)
        elif isinstance(value, SingleVectorComponent):
            return SingleVectorComponent(
                remap_var_name(value.vector_name),
                value.component_name,
                value.scalar_type,
                value.negated
            )
        elif isinstance(value, VectorValueBase):
            return VectorValue([remap_value(comp) for comp in value.scalar_values], value.negated)
        return value
    def transform_single(a: Action):
        return Action(a.func, [remap_value(v) for v in a.remapped_in])
    def transform(actions: List[Action]) -> List[Action]:
        transform_single = lambda a: Action(
            a.f
        )
        new_actions = [

        ]

    return transform"""
