from typing import Union, Tuple, overload, Callable

from dxbc.Errors import DXBCError
from dxbc.v2.types import ScalarType
from dxbc.v2.values import ScalarValueBase, VectorValueBase, Value, VectorValue


def map_scalar_values(f: Callable[[ScalarValueBase], ScalarValueBase], value: Value) -> Value:
    if isinstance(value, ScalarValueBase):
        return f(value)
    elif isinstance(value, VectorValueBase):
        return VectorValue([f(scalar) for scalar in value.scalar_values], False)


def get_type_string(scalar_type: ScalarType, count: int):
    if count == 1:
        return scalar_type.name()
    return f"{scalar_type.name()}{count}"


@overload
def trim_components(vec: VectorValueBase, component_count: int) -> VectorValueBase:
    pass

@overload
def trim_components(vec: ScalarValueBase, component_count: int) -> ScalarValueBase:
    pass

def trim_components(vec: Union[ScalarValueBase, VectorValueBase], component_count: int):
    if isinstance(vec, ScalarValueBase):
        if component_count != 1:
            raise DXBCError("Scalars can only be trimmed to 1 component")
        return vec

    new_components = vec.scalar_values
    if len(new_components) < component_count or component_count <= 0:
        raise DXBCError("Invalid argument to trim_components, tried to trim vector with {} comps to {}".format(
            len(new_components), component_count))

    if component_count == 1:
        return new_components[0]
    # Promote to SwizzledVectorValue if possible
    # (in case something like (a.x, a.y, a.z, 1.0) is trimmed to 3 components)
    return VectorValue(new_components[0:component_count], negated=vec.negated)


@overload
def mask_components(vec: ScalarValueBase, component_mask: Tuple[bool, bool, bool, bool]) -> ScalarValueBase:
    pass

@overload
def mask_components(vec: VectorValueBase, component_mask: Tuple[bool, bool, bool, bool]) -> Value:
    pass

def mask_components(vec: Union[ScalarValueBase, VectorValueBase], component_mask: Tuple[bool, bool, bool, bool]) -> Value:
    if isinstance(vec, ScalarValueBase):
        if sum(component_mask) != 1:
            raise DXBCError(f"Scalars can only be masked to one component, attempted {component_mask}")
        return vec

    new_components = []
    try:
        for (i, mask) in enumerate(component_mask):
            if mask:
                new_components.append(vec.scalar_values[i])
    except IndexError:
        raise DXBCError("Tried to unmask components that didn't exist. mask: {}, scalar_values: {}".format(
            component_mask, vec.scalar_values
        ))
    if len(new_components) == 0:
        raise DXBCError("Masked out all components of vector")
    elif len(new_components) == 1:
        return new_components[0]
    return VectorValue(new_components, negated=vec.negated)
