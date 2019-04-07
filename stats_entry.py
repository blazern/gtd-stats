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
    # Collect entries by date
    entries_mapped_by_date = {}
    for entry in entries:
      if entry.date not in entries_mapped_by_date:
        entries_mapped_by_date[entry.date] = []
      entries_mapped_by_date[entry.date].append(entry)

    result = []
    for date, day_entries in entries_mapped_by_date.items():
      # Collect (already collected by date) entries by description
      day_entries_mapped_by_descr = {}
      for day_entry in day_entries:
        if day_entry.description not in day_entries_mapped_by_descr:
           day_entries_mapped_by_descr[day_entry.description] = []
        day_entries_mapped_by_descr[day_entry.description].append(day_entry)

      # Collapse entries with same date and description
      for description, descr_entries in day_entries_mapped_by_descr.items():
        sum_value = 0
        for descr_entry in descr_entries:
          sum_value += descr_entry.value
        result.append(StatsEntry(date, sum_value, description))

    result = sorted(result, key=lambda entry: entry.date) 
    return result