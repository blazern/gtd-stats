from datetime import datetime

from core.stats.stats_entry import StatsEntry
from core.stats.stat_column_type import StatColumnType

def _TypedStatsEntry__normalize_date(date):
  # Remove hours, minutes, seconds, etc
  return _TypedStatsEntry__str_to_date(_TypedStatsEntry__date_to_str(date))

def _TypedStatsEntry__date_to_str(date):
  return date.strftime('%d/%m/%Y')

def _TypedStatsEntry__str_to_date(date_str):
  return datetime.strptime(date_str, '%d/%m/%Y')

def _TypedStatsEntry__typed_column_to_str(stat_column_type, typed_column):
  if stat_column_type is StatColumnType.DATE:
    if not isinstance(typed_column, datetime):
      raise ValueError('Value {} was expected to be a datetime'.format(typed_column))
    return _TypedStatsEntry__date_to_str(typed_column)
  elif stat_column_type is StatColumnType.ID or stat_column_type is StatColumnType.COMMENT:
    if not isinstance(typed_column, str):
      raise ValueError('Value {} was expected to be a str'.format(typed_column))
    return typed_column
  elif stat_column_type is StatColumnType.VALUE:
    if not isinstance(typed_column, float) and not isinstance(typed_column, int):
      raise ValueError('Value {} was expected to be a float or int'.format(typed_column))
    return '%g'%(typed_column)
  else:
    raise ValueError('Unexpected type {} for column {}'.format(stat_column_type, typed_column))

class TypedStatsEntry:
  def __init__(self, stats_entry, types):
    if not isinstance(types, list):
      raise ValueError('Types are expected to be a list, but is {}'.format(type(types)))
    self.not_typed = stats_entry
    self.types = types

  @staticmethod
  def from_stats(stat_column_types, typed_columns):
    columns = []
    for indx, typed_column in enumerate(typed_columns):
      columns.append(__typed_column_to_str(stat_column_types[indx], typed_column))
    return TypedStatsEntry(StatsEntry(columns), stat_column_types)

  def value(self):
    result = self.__get_column_of_type(StatColumnType.VALUE)
    if result is None:
      return None
    return float(result)

  def comment(self):
    return self.__get_column_of_type(StatColumnType.COMMENT)

  def id(self):
    return self.__get_column_of_type(StatColumnType.ID)

  def date(self):
    result = self.__get_column_of_type(StatColumnType.DATE)
    if result is None:
      return None
    return __str_to_date(result)

  def __get_column_of_type(self, stat_column_type):
    indexes = []
    for indx, curr_stat_column_type in enumerate(self.types):
      if curr_stat_column_type is stat_column_type:
        indexes.append(indx)
    if len(indexes) == 0:
      return None
    if len(indexes) > 1:
      raise ValueError('Number of columns with type {} != 1. Indexes: {}, types: {}'.format(stat_column_type, indexes, self.types))
    return self.not_typed.columns[indexes[0]]

  def at(self, indx):
    stat_column_type = self.types[indx]
    if stat_column_type is StatColumnType.DATE:
      return __str_to_date(self.not_typed.columns[indx])
    elif stat_column_type is StatColumnType.ID or stat_column_type is StatColumnType.COMMENT:
      return self.not_typed.columns[indx]
    elif stat_column_type is StatColumnType.VALUE:
      return float(self.not_typed.columns[indx])
    else:
      raise ValueError('Unexpected StatColumnType: {}'.format(stat_column_type))

  def __str__(self):
    return str(self.not_typed)