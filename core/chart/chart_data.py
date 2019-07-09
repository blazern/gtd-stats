from core.stats.stats_entry import StatsEntry

from datetime import timedelta
from itertools import *

from core.stats.stats_metadata import StatsMetadata
from core.stats.stat_column_type import StatColumnType

def _ChartLineData__stats_entries_to_x_y_data(stats_entries, value_column_index, earliest_date):
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
    value = stats_entries[index].at(value_column_index)
    if value is None:
      value = 1
    y.append(value)
    prev_date = curr_date
  if x[0] != earliest_date:
    x = [earliest_date] + x
    y = [0] + y
  return x, y

def _ChartData__cluster_to_chart_line_seeds(cluster):
  result = []

  types = cluster.metadata().types()
  types_extras = cluster.metadata().types_extras()
  values_indexes = []
  for indx, column_type in enumerate(cluster.metadata().types()):
    if column_type is StatColumnType.VALUE:
      values_indexes.append(indx)
  if len(values_indexes) == 0:
    raise ValueError('No VALUE column in cluster, can\'t produce x y data. Cluster: {}'.format(str(cluster)))
  if len(values_indexes) > 1:
    for indx in values_indexes:
      type_extra = types_extras[indx]
      if not isinstance(type_extra, str) or len(type_extra) == 0:
        raise ValueError(('Invalid VALUE extra at index {}. '
          + 'If there\'re more than 1 value, all values extras must be not empty. '
          + 'Cluster: {}').format(indx, str(cluster)))

  entries = list(cluster.typed_entries())
  earliest_date = min([entry.date() for entry in entries])

  entry_id_func = lambda entry: entry.id()
  if StatColumnType.ID in types:
    entries = sorted(entries, key=entry_id_func)
  for entries_group_id, entries_group in groupby(entries, entry_id_func):
    entries_group = list(entries_group)
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
  return result

class ChartData:
  def __init__(self, stats_cluster):
    self._lines = []
    line_seeds = __cluster_to_chart_line_seeds(stats_cluster)
    for seed in line_seeds:
      self._lines.append(ChartLineData(seed))

  def lines(self):
    return self._lines

class ChartLineData:
  def __init__(self, seed):
    self._title = seed.title
    self._xcoords, self._ycoords = __stats_entries_to_x_y_data(seed.entries,
                                                               seed.value_column_index,
                                                               seed.earliest_date)

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