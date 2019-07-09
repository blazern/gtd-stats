import sys
import yaml

from core.stats.stat_column_type import StatColumnType
from core.chart.chart_appearance import *

class StatsMetadata:
  def __init__(self, stat_column_types, stat_column_types_extras=None, chart_appearances=[]):
    if stat_column_types_extras is None:
      stat_column_types_extras = [None for column_type in stat_column_types]
    if len(stat_column_types) != len(stat_column_types_extras):
      raise ValueError('Sizes of types and extras must be equal: {}, {}'.format(
        stat_column_types, stat_column_types_extras))
    self._stat_column_types = stat_column_types
    self._stat_column_types_extras = stat_column_types_extras
    self._chart_appearances = chart_appearances

  def types(self):
    return list(self._stat_column_types)

  def types_extras(self):
    return list(self._stat_column_types_extras)

  def chart_appearances(self):
    return list(self._chart_appearances)

  @staticmethod
  def from_str(string):
    types, types_extras, appearances = StatsMetadata._extract_types_and_appearances(string)
    return StatsMetadata(types, types_extras, appearances)

  @staticmethod
  def _extract_types_and_appearances(string):
    if string.strip().startswith('==='):
      return StatsMetadata._extract_types_and_appearances_complex(string)
    else:
      return StatsMetadata._extract_types_and_appearances_simple(string)
  
  @staticmethod
  def _extract_types_and_appearances_simple(string):
    types, types_extras = StatsMetadata._parse_types_data(string.strip())
    return types, types_extras, []

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
  def _extract_types_and_appearances_complex(string):
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
    appearances = []
    for metadata_entry in metadata_dict:
      if metadata_entry['what'] == 'format':
        types, types_extras = StatsMetadata._parse_types_data(metadata_entry['value'])
      elif metadata_entry['what'] == 'chart':
        title = metadata_entry['title']
        if 'types' in metadata_entry:
          if len(metadata_entry) != 3:
            raise ValueError('Size of appearance with "types" param expected to be 3. Entry: '.format(metadata_entry))
          modifiers_dicts = metadata_entry['types']
        else:
          modifiers_dicts = [metadata_entry]
        modifiers = []
        for modifier_dict in modifiers_dicts:
          if modifier_dict['type'] == 'moving-average':
            offset = modifier_dict['offset']
            modifiers.append(MovingAverageChartAppearanceModifier(offset))
          elif modifier_dict['type'] == 'period':
            unit = modifier_dict['unit']
            if unit == 'days':
              unit = PeriodChartAppearanceModifier.Unit.DAY
            elif unit == 'months':
              unit = PeriodChartAppearanceModifier.Unit.MONTH
            elif unit == 'years':
              unit = PeriodChartAppearanceModifier.Unit.YEAR
            else:
              raise ValueError('Unknown time unit: {}'.format(unit))
            unit_value = modifier_dict['unit-value']
            modifiers.append(PeriodChartAppearanceModifier(unit, unit_value))
          else:
            raise ValueError('Unexpected chart appearance type in: {}'.format(modifier_dict))
        appearances.append(ChartAppearance(title, modifiers))
    return types, types_extras, appearances

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
    if len(self._chart_appearances) == 0:
      return self._types_to_str()

    self_yaml_list = []
    for appearance in self._chart_appearances:
      appearance_dict = {}
      appearance_dict['what'] = 'chart'
      appearance_dict['title'] = appearance.title
      modifiers_dicts = []
      for modifier in appearance.modifiers:
        modifier_dict = {}
        if isinstance(modifier, MovingAverageChartAppearanceModifier):
          modifier_dict['type'] = 'moving-average'
          modifier_dict['offset'] = modifier.offset
        elif isinstance(modifier, PeriodChartAppearanceModifier):
          modifier_dict['type'] = 'period'
          if modifier.time_unit is PeriodChartAppearanceModifier.Unit.DAY:
            modifier_dict['unit'] = 'days'
          elif modifier.time_unit is PeriodChartAppearanceModifier.Unit.MONTH:
            modifier_dict['unit'] = 'months'
          elif modifier.time_unit is PeriodChartAppearanceModifier.Unit.YEAR:
            modifier_dict['unit'] = 'years'
          else:
            raise ValueError('Unknown time unit: {}'.format(modifier.time_unit))
          modifier_dict['unit-value'] = modifier.time_period_size
        modifiers_dicts.append(modifier_dict)
      if len(modifiers_dicts) == 1:
        for key, value in modifiers_dicts[0].items():
          appearance_dict[key] = value
      else:
        appearance_dict['types'] = modifiers_dicts
      self_yaml_list.append(appearance_dict)
    self_yaml_list.append({'what':'format', 'value':self._types_to_str()})
    return '===\n{}==='.format(yaml.dump(self_yaml_list, sort_keys=False))

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