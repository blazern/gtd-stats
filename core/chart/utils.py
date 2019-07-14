from core.chart.modifiers.chart_modifiers_composite import *
from core.chart.modifiers.moving_average_chart_modifier import *
from core.chart.modifiers.period_chart_modifier import *

def extract_chart_modifiers_from_stats_metadata(metadata):
  raw_metadata = metadata.raw_metadata()
  modifiers = []
  for metadata_entry in raw_metadata:
    if metadata_entry['what'] == 'chart':
      title = metadata_entry['title']
      if 'types' in metadata_entry:
        if len(metadata_entry) != 3:
          raise ValueError('Size of modifier with "types" param expected to be 3. Entry: '.format(metadata_entry))
        submodifiers_dicts = metadata_entry['types']
      else:
        submodifiers_dicts = [metadata_entry]
      submodifiers = []
      for modifier_dict in submodifiers_dicts:
        if modifier_dict['type'] == 'moving-average':
          offset = modifier_dict['offset']
          submodifiers.append(MovingAverageChartModifier(offset))
        elif modifier_dict['type'] == 'period':
          unit = modifier_dict['unit']
          if unit == 'days':
            unit = PeriodChartModifier.Unit.DAY
          elif unit == 'months':
            unit = PeriodChartModifier.Unit.MONTH
          elif unit == 'years':
            unit = PeriodChartModifier.Unit.YEAR
          else:
            raise ValueError('Unknown time unit: {}'.format(unit))
          unit_value = modifier_dict['unit-value']
          submodifiers.append(PeriodChartModifier(unit, unit_value))
        else:
          raise ValueError('Unexpected chart modifier type in: {}'.format(modifier_dict))
      modifiers.append(ChartModifiersComposite(title, submodifiers))
  return modifiers