import collections

Action = collections.namedtuple('Action', 'func remapped_in remapped_out new_variable new_state')
