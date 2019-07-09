import re
import math
from datetime import datetime

class StatsEntry:
  def __init__(self, columns):
    self.columns = columns

  def __str__(self):
    return ';'.join(self.columns)

  @staticmethod
  def from_str(string):
    columns = string.split(';')
    return StatsEntry(columns)

  def __eq__(self, other):
    if isinstance(other, StatsEntry):
      return self.columns == other.columns
    return False
