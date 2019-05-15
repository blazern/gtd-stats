from core.stat_column_type import StatColumnType

class StatsMetadata:
  def __init__(self, stat_column_types):
    self._stat_column_types = stat_column_types

  def types(self):
    return list(self._stat_column_types)

  @staticmethod
  def from_str(string):
    types_strs = string.split(';')
    types = []
    for type_str in types_strs:
      types.append(StatColumnType.from_str(type_str))
    return StatsMetadata(types)

  def __str__(self):
    stat_column_types_strs = []
    for stat_column_type in self._stat_column_types:
      stat_column_types_strs.append(str(stat_column_type))
    return ';'.join(stat_column_types_strs)

  def __eq__(self, other):
    if isinstance(other, StatsMetadata):
      return self._stat_column_types == other._stat_column_types
    return False