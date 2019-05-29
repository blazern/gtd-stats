from core.typed_stats_entry import TypedStatsEntry
from core.stats_metadata import StatsMetadata
from core.stats_entry import StatsEntry
from core.stat_column_type import StatColumnType

def _StatsCluster__entries_to_typed_entries(metadata, stats_entries):
  result = []
  for entry in stats_entries:
    result.append(TypedStatsEntry(entry, metadata.types()))
  return result

class StatsCluster:
  def __init__(self, metadata, stats_entries, typed_stats_entries=None):
    if typed_stats_entries is not None:
      if len(typed_stats_entries) != len(stats_entries):
        raise ValueError('Given typed stats entries differ from not typed: {}, {}'.format(typed_stats_entries, stats_entries))
      for indx, typed_entry in enumerate(typed_stats_entries):
        if stats_entries[indx] != typed_stats_entries[indx].not_typed:
          raise ValueError('Given typed stats entries differ from not typed: {}, {}'.format(typed_stats_entries, stats_entries))
    self._metadata = metadata
    self._stats_entries = stats_entries
    self._typed_stats_entries = typed_stats_entries
    if self._typed_stats_entries is None:
      self._typed_stats_entries = __entries_to_typed_entries(metadata, stats_entries)

    # Sorting
    self._typed_stats_entries = sorted(self._typed_stats_entries, key=lambda entry: entry.date(), reverse=True)
    # Constructing sorted not-typed entries list
    stats_entries = []
    for entry in self._typed_stats_entries:
      stats_entries.append(entry.not_typed)
    self._stats_entries = stats_entries

  @staticmethod
  def from_typed_entries(typed_entries, metadata):
    entries = []
    for typed_entry in typed_entries:
      entries.append(typed_entry.not_typed)
    return StatsCluster(metadata, entries, typed_entries)

  @staticmethod
  def from_str(string):
    lines = string.split('\n')
    lines = [line for line in lines if len(line.strip()) > 0]
    string = '\n'.join(lines)

    first_line_break = string.find('\n')
    if first_line_break >= 0:
      metadata_start, metadata_end = StatsMetadata.find_str_position(string)
      metadata_str = string[metadata_start:metadata_end]
      all_entries_str = string[0:metadata_start]+string[metadata_end:]
    else:
      metadata_str = string
      all_entries_str = ''

    entries_strs = all_entries_str.split('\n')
    entries_strs = [entry.strip() for entry in entries_strs]
    entries_strs = [entry for entry in entries_strs if len(entry) > 0]
    entries = []
    for entry_str in entries_strs:
      entries.append(StatsEntry.from_str(entry_str))
    return StatsCluster(StatsMetadata.from_str(metadata_str), entries)
 
  def __str__(self):
    metadata_str = str(self._metadata)
    entries_strs = []
    for entry in self._stats_entries:
      entries_strs.append(str(entry))
    return '\n'.join([metadata_str] + entries_strs)

  def type_at(self, indx):
    return self._metadata.types()[indx]

  def typed_entries(self):
    return list(self._typed_stats_entries)

  def entries(self):
    return list(self._stats_entries)

  def metadata(self):
    return self._metadata

  def collapse(self):
    entries_dict = {}
    for entry in self._typed_stats_entries:
      # Note that currently we support only single date and single id
      date_id_pair = (entry.date(), entry.id())
      if date_id_pair not in entries_dict:
        entries_dict[date_id_pair] = []
      entries_dict[date_id_pair].append(entry)

    result_typed_entries = []
    for date_id_pair, same_date_id_entries in entries_dict.items():
      # For simplicity, creating a list with same size as there are columns
      sum_values = [0.] * len(self._metadata.types())
      sum_comments = [''] * len(self._metadata.types())

      # Summing
      for entry in same_date_id_entries:
        for indx, stat_column_type in enumerate(self._metadata.types()):
          if stat_column_type is StatColumnType.VALUE:
            sum_values[indx] += entry.at(indx)
          elif stat_column_type is StatColumnType.COMMENT:
            sum_comments += entry.at(indx) + ' '
          elif stat_column_type is StatColumnType.ID or stat_column_type is StatColumnType.DATE:
            pass # Pass, because we already constructed map with ID+DATE pairs
          else:
            raise ValueError('Unknown StatColumnType: {}'.format(stat_column_type))

      # Constructing collapsed entry
      result_columns = []
      for indx, stat_column_type in enumerate(self._metadata.types()):
        if stat_column_type is StatColumnType.VALUE:
          result_columns.append('%g'%(sum_values[indx]))
        elif stat_column_type is StatColumnType.COMMENT:
          result_columns.append(sum_comments[indx])
        elif stat_column_type is StatColumnType.ID or stat_column_type is StatColumnType.DATE:
          result_columns.append(same_date_id_entries[0].not_typed.columns[indx])
        else:
          raise ValueError('Unknown StatColumnType: {}'.format(stat_column_type))
      result_typed_entries.append(TypedStatsEntry(StatsEntry(result_columns), self._metadata.types()))

    result_entries = []
    for typed_entry in result_typed_entries:
      result_entries.append(typed_entry.not_typed)
    return StatsCluster(self._metadata, result_entries, result_typed_entries)

  # Self an passed Cluster both must be collapsed
  def merge(self, other, prioritized):
    # Verifying collapsed state
    if len(self._stats_entries) != len(self.collapse()._stats_entries):
      raise ValueError('Self is not collapsed: {}'.format(self._stats_entries))
    if len(other._stats_entries) != len(other.collapse()._stats_entries):
      raise ValueError('Other cluster is not collapsed: {}'.format(other.stats_entries))
    if self._metadata != other._metadata:
      raise ValueError('Metadata of both clusters must be same, but it isn\'t: {}, {}'.format(self._metadata, other._metadata))

    # Aquiring prioritized and not prioritized refs
    if self is prioritized:
      notprioritized = other
    elif other is prioritized:
      notprioritized = self
    else:
      raise ValueError('One of the given clusters must be prioritized')

    # Filling merged entries dict with prioritized entries
    merged_entries_dict = {}
    for entry in prioritized.typed_entries():
      date_id_pair = (entry.date(), entry.id())
      # Note that we asserted in the beginning of the function
      # that both clusters are already collapsed.
      if date_id_pair in merged_entries_dict:
        raise RuntimeError('Unexpectedly collapsing didn\'t work: {}', prioritized)
      merged_entries_dict[date_id_pair] = entry

    # Filling merged entries dict with not prioritized entries
    for entry in notprioritized.typed_entries():
      date_id_pair = (entry.date(), entry.id())
      if date_id_pair not in merged_entries_dict:
        merged_entries_dict[date_id_pair] = entry

    typed_entries = []
    for entry in merged_entries_dict.values():
      typed_entries.append(entry)

    merged_entries = []
    for entry in typed_entries:
      merged_entries.append(entry.not_typed)

    return StatsCluster(self._metadata, merged_entries, typed_entries)