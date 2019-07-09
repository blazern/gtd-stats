from enum import Enum, auto

class StatColumnType(Enum):
  DATE = auto()
  VALUE = auto()
  ID = auto()
  COMMENT = auto()

  def __str__(self):
    return self.name.lower()

  @staticmethod
  def from_str(string):
    for stat_column_type in StatColumnType:
      if str(stat_column_type) == string:
        return stat_column_type
    raise ValueError('Invalid string for StatColumnType: {}'.format(string))