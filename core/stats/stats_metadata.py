import copy
import sys
import yaml

from core.stats.stat_column_type import StatColumnType

class StatsMetadata:
  def __init__(self, stat_column_types, stat_column_types_extras=None, raw_metadata={}):
    if stat_column_types_extras is None:
      stat_column_types_extras = [None for column_type in stat_column_types]
    if len(stat_column_types) != len(stat_column_types_extras):
      raise ValueError('Sizes of types and extras must be equal: {}, {}'.format(
        stat_column_types, stat_column_types_extras))
    self._stat_column_types = stat_column_types
    self._stat_column_types_extras = stat_column_types_extras
    self._raw_metadata = raw_metadata

  def types(self):
    return list(self._stat_column_types)

  def types_extras(self):
    return list(self._stat_column_types_extras)

  # YAML text converted to a Python object (list of dicts).
  # The function always returns a copy - feel free to modify it.
  def raw_metadata(self):
    return copy.deepcopy(self._raw_metadata)

  @staticmethod
  def from_str(string):
    types, types_extras, raw_metadata = StatsMetadata._extract_types_and_raw_metadata(string)
    return StatsMetadata(types, types_extras, raw_metadata)

  @staticmethod
  def _extract_types_and_raw_metadata(string):
    if string.strip().startswith('==='):
      return StatsMetadata._extract_types_and_raw_metadata_complex(string)
    else:
      return StatsMetadata._extract_types_and_raw_metadata_simple(string)
  
  @staticmethod
  def _extract_types_and_raw_metadata_simple(string):
    types, types_extras = StatsMetadata._parse_types_data(string.strip())
    return types, types_extras, {}

  @staticmethod
  def _parse_types_data(string):
    types_strs = string.split(';')
    types = []
    types_extras = []
    for type_str in types_strs:
      type_and_extra = type_str.split(':')
      types.append(StatColumnType.from_str(type_and_extra[0]))
      if len(type_and_extra) == 1:
        types_extras.append(None)
      elif len(type_and_extra) == 2:
        types_extras.append(type_and_extra[1])
      else:
        raise ValueError('Invalid size of type_and_extra: {}'.format(type_and_extra))
    return types, types_extras

  @staticmethod
  def _extract_types_and_raw_metadata_complex(string):
    if not string.strip().endswith('==='):
      raise ValueError('Metadata str starts with === but doesn\'t end with it: {}'.format(string))
    lines = string.strip().split('\n')
    if lines[0].strip() != '===':
      raise ValueError('First line must have only === in metadata, but has: {}'.format(lines[0]))
    if lines[-1].strip() != '===':
      raise ValueError('Last line must have only === in metadata, but has: {}'.format(lines[-1]))
    string = '\n'.join(lines[1:-1])
    
    if sys.version_info[0] < 3 and sys.version_info[1] < 7:
      raise EnvironmentError('Because of dict ordering guarantees, python 3.7 required ({} was run).'.format(sys.version_info)
                             + ' See https://docs.python.org/3/whatsnew/3.7.html')
    metadata_dict = yaml.safe_load(string)
    types = None
    types_extras = None
    for metadata_entry in metadata_dict:
      if metadata_entry['what'] == 'format':
        types, types_extras = StatsMetadata._parse_types_data(metadata_entry['value'])
        break
    if types is None:
      raise ValueError('No types in given string: {}'.format(string))
    return types, types_extras, metadata_dict

  @staticmethod
  def find_str_position(string):
    if string.strip().startswith('==='):
      start = 0
      end = string.find('===', 1) + 3
    elif string.strip().endswith('==='):
      last_border_indx = string.rfind('===')
      start = string.rfind('===', 0, last_border_indx)
      end = len(string)
    else:
      start = 0
      end = string.find('\n')
      if end == -1:
        end = len(string)
    return start, end

  def __eq__(self, other):
    if isinstance(other, StatsMetadata):
      return str(self) == str(other)
    return False

  def __str__(self):
    if len(self._raw_metadata) == 0:
      return self._types_to_str()
    return '===\n{}==='.format(yaml.dump(self._raw_metadata, sort_keys=False))

  def _types_to_str(self):
    stat_column_types_strs = []
    for i in range(len(self._stat_column_types)):
      type_str = str(self._stat_column_types[i])
      if self._stat_column_types_extras[i] is not None:
        type_extra_str = ':{}'.format(self._stat_column_types_extras[i])
      else:
        type_extra_str = ''
      stat_column_types_strs.append(type_str+type_extra_str)
    return ';'.join(stat_column_types_strs)