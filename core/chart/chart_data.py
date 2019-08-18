from core.stats.stats_entry import StatsEntry

from collections import OrderedDict
from datetime import timedelta
from itertools import *

from core.stats.stats_metadata import StatsMetadata
from core.stats.stat_column_type import StatColumnType

def _ChartData__stats_to_chart_line_seeds(typed_entries, metadata):
  result = []

  types = metadata.types()
  types_extras = metadata.types_extras()
  values_indexes = []
  for indx, column_type in enumerate(types):
    if column_type is StatColumnType.VALUE:
      values_indexes.append(indx)
  if len(values_indexes) > 1:
    for indx in values_indexes:
      type_extra = types_extras[indx]
      if not isinstance(type_extra, str) or len(type_extra) == 0:
        raise ValueError(('Invalid VALUE extra at index {}. '
          + 'If there\'re more than 1 value, all values extras must be not empty. '
          + 'Metadata: {}').format(indx, str(metadata)))

  entries = list(typed_entries)
  earliest_date = min([entry.date() for entry in entries])

  entry_id_func = lambda entry: entry.id()
  if StatColumnType.ID in types:
    entries = sorted(entries, key=entry_id_func)
  for entries_group_id, entries_group in groupby(entries, entry_id_func):
    entries_group = list(entries_group)
    if len(values_indexes) > 0:
      for indx in values_indexes:
        if types_extras[indx] is None and entries_group_id is None:
          title = ''
        elif types_extras[indx] is None and entries_group_id is not None:
          title = entries_group_id
        elif types_extras[indx] is not None and entries_group_id is None:
          title = types_extras[indx]
        elif types_extras[indx] is not None and entries_group_id is not None:
          title = '{}_{}'.format(entries_group_id, types_extras[indx])
        else:
          raise ValueError('Invalid state')
        result.append(_ChartLineSeed(entries_group, title, indx, earliest_date))
    else:
      title = entries_group_id
      if title is None:
        title = 'value'
      result.append(_ChartLineSeed(entries_group, title, None, earliest_date))
  return result

class ChartData:
  def __init__(self, stats_cluster, chart_modifier=None, title_base=''):
    self._lines = []
    typed_entries, metadata = stats_cluster.typed_entries(), stats_cluster.metadata()
    line_seeds = __stats_to_chart_line_seeds(typed_entries, metadata)
    for seed in line_seeds:
      self._lines.append(seed.grow())
    if chart_modifier is not None:
      self._lines = chart_modifier.convert_lines(self._lines)
      self._title = '{}_{}'.format(title_base, chart_modifier.title)
    else:
      self._title = title_base

  def lines(self):
    return self._lines

  def title(self):
    return self._title

class ChartLineData:
  def __init__(self, title, x_coords, y_coords):
    self._title = title
    self._xcoords = x_coords
    self._ycoords = y_coords

  def title(self):
    return self._title

  def x_coords(self):
    return self._xcoords

  def y_coords(self):
    return self._ycoords

class _ChartLineSeed:
  def __init__(self, entries, title, value_column_index, earliest_date):
    self.entries = entries
    self.title = title
    self.value_column_index = value_column_index
    self.earliest_date = earliest_date

  def grow(self):
    xcoords, ycoords = self.stats_entries_to_x_y_data(self.entries,
                                                      self.value_column_index,
                                                      self.earliest_date)
    return ChartLineData(self.title, xcoords, ycoords)

  def stats_entries_to_x_y_data(self, stats_entries, value_column_index, earliest_date):
    if len(stats_entries) == 0:
      return [], []
    stats_entries = sorted(stats_entries, key=lambda entry: entry.date())
    x = []
    y = []
    prev_date = earliest_date
    for index in range(0, len(stats_entries)):
      curr_date = stats_entries[index].date()
      days_diff = (curr_date - prev_date).days
      if days_diff > 1:
        for day_index in range(1, days_diff):
          mid_date = prev_date + timedelta(days=day_index)
          x.append(mid_date)
          y.append(0)
      x.append(curr_date)
      if value_column_index is not None:
        value = stats_entries[index].at(value_column_index)
      else:
        value = 1
      y.append(value)
      prev_date = curr_date
    if x[0] != earliest_date:
      x = [earliest_date] + x
      y = [0] + y

    x, y = self.merge_values_with_same_x(x, y)
    return x, y

  def merge_values_with_same_x(self, x, y):
    merging_coods = OrderedDict()
    for indx in range(0, len(x)):
      if x[indx] not in merging_coods:
        merging_coods[x[indx]] = 0
      merging_coods[x[indx]] += y[indx]
    x_final = []
    y_final = []
    for x_key, y_val in merging_coods.items():
      x_final.append(x_key)
      y_final.append(y_val)
    return x_final, y_final