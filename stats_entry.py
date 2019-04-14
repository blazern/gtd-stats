import re
import math
from datetime import datetime

def _StatsEntry__normalize_date(date):
  # Remove hours, minutes, seconds, etc
  return _StatsEntry__str_to_date(_StatsEntry__date_to_str(date))

def _StatsEntry__date_to_str(date):
  return date.strftime('%d/%m/%Y')

def _StatsEntry__str_to_date(date_str):
  return datetime.strptime(date_str, '%d/%m/%Y')

class StatsEntry:
  def __init__(self, date, value, description):
    self.date = __normalize_date(date)
    self.value = value
    self.description = description

  def __str__(self):
    date_str = __date_to_str(self.date)
    return '{};{};{}'.format(date_str, self.value, self.description)

  @staticmethod
  def from_str(string):
    str_pattern = re.compile("^\d\d\/\d\d/\d\d\d\d;\d+;.*$")
    if not str_pattern.match(string):
      raise ValueError('Invalid stats entry str: {}'.format(string))

    value_index = string.index(';') + 1
    description_index = string.index(';', value_index) + 1

    return StatsEntry(__str_to_date(string[:value_index - 1]),
                      int(string[value_index:description_index - 1]),
                      string[description_index:])

  def __eq__(self, other):
    if isinstance(other, StatsEntry):
        return self.date == other.date \
               and math.isclose(self.value, other.value, abs_tol=0.001) \
               and self.description == other.description
    return False

  @staticmethod
  def collapse(entries):
    entries_dict = {}
    for entry in entries:
      date_descr_pair = (entry.date, entry.description)
      if date_descr_pair not in entries_dict:
        entries_dict[date_descr_pair] = []
      entries_dict[date_descr_pair].append(entry)

    result = []
    for date_descr_pair, same_date_descr_entries in entries_dict.items():
      sum_value = 0
      for entry in same_date_descr_entries:
        sum_value += entry.value
      result.append(StatsEntry(date_descr_pair[0], sum_value, date_descr_pair[1]))
    result = sorted(result, key=lambda entry: entry.date) 
    return result

  # Passed entries must be collapsed
  @staticmethod
  def merge(entries1, entries2, prioritized):
    if len(entries1) != len(StatsEntry.collapse(entries1)):
      raise ValueError('First entries list is not collapsed: {}'.format(entries1))
    if len(entries2) != len(StatsEntry.collapse(entries2)):
      raise ValueError('Second entries list is not collapsed: {}'.format(entries1))

    if entries1 is prioritized:
      notprioritized = entries2
    elif entries2 is prioritized:
      notprioritized = entries1
    else:
      raise ValueError('One of the given lists must be prioritized')

    merged_entries_dict = {}
    for entry in prioritized:
      date_descr_pair = (entry.date, entry.description)
      # Note that we asserted in the beginning of the function
      # that both lists are already collapsed.
      if date_descr_pair in merged_entries_dict:
        raise RuntimeError('Unexpectedly collapsing didn\t work: {}', prioritized)
      merged_entries_dict[date_descr_pair] = entry

    for entry in notprioritized:
      date_descr_pair = (entry.date, entry.description)
      if date_descr_pair not in merged_entries_dict:
        merged_entries_dict[date_descr_pair] = entry

    merged_entries = []
    for entry in merged_entries_dict.values():
      merged_entries.append(entry)
    merged_entries = sorted(merged_entries, key=lambda entry: entry.date)
    return merged_entries