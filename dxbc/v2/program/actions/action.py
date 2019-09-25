import collections
import typing

from dxbc.v2.program.functions import Function
from dxbc.v2.program.modifiers import Modifier
from dxbc.v2.program.state import ExecutionState
from dxbc.v2.values import Value

Action = typing.NamedTuple("Action",
                           [
                               ("func", Function),
                               ("remapped_in", typing.List[Value]),
                               ("remapped_out", typing.Optional[Value]),
                               ("new_variable", bool),
                               ("new_state", ExecutionState),
                               ("modifier", typing.Optional[Modifier])
                           ]
                           )

