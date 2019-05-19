from core.stats_entry import StatsEntry

from datetime import timedelta
from itertools import *

from core.stats_metadata import StatsMetadata
from core.stat_column_type import StatColumnType

def _ChartLineData__stats_entries_to_x_y_data(metadata, stats_entries):
  if len(stats_entries) == 0:
    return [], []
  stats_entries = sorted(stats_entries, key=lambda entry: entry.date())
  x = []
  y = []
  prev_date = None
  for index in range(0, len(stats_entries)):
    if prev_date is None:
      prev_date = stats_entries[index].date()
      x.append(stats_entries[index].date())
      y.append(stats_entries[index].value())
      continue
    curr_date = stats_entries[index].date()
    days_diff = (curr_date - prev_date).days
    if days_diff > 1:
      for day_index in range(1, days_diff):
        mid_date = prev_date + timedelta(days=day_index)
        x.append(mid_date)
        y.append(0)
    x.append(curr_date)
    y.append(stats_entries[index].value())
    prev_date = curr_date
  return x, y

class ChartData:
  def __init__(self, stats_cluster):
    if StatColumnType.VALUE not in stats_cluster.metadata().types():
      raise ValueError('Can\'t create a chart without values. Metadata: {}'.format(str(metadata)))
    self._lines = []

    if StatColumnType.ID in stats_cluster.metadata().types():
      entries = list(stats_cluster.typed_entries())
      entry_id_func = lambda entry: entry.id()
      entries = sorted(entries, key=entry_id_func)
      for entries_group_id, entries_group in groupby(entries, entry_id_func):
        entries_group = list(entries_group)
        self._lines.append(ChartLineData(stats_cluster.metadata(), list(entries_group), title=entries_group_id))
    else:
      self._lines.append(ChartLineData(stats_cluster.metadata(), stats_cluster.entries(), title=''))

  def lines(self):
    return self._lines

class ChartLineData:
  def __init__(self, metadata, entries, title):
    self._title = title
    self._xcoords, self._ycoords = __stats_entries_to_x_y_data(metadata, entries)

  def title(self):
    return self._title

  def x_coords(self):
    return self._xcoords

  def y_coords(self):
    return self._ycoords