from core.chart.chart_appearance import *


def _ChartsFamily__cluster_to_charts_data(stats_cluster):
  # TODO: first parse all chart_modifiers and stats_modifiers,
  # TODO: TODO: what second?
  metadata_dict = stats_cluster.metadata().raw_metadata_dict()
  appearances = []
  for metadata_entry in metadata_dict:
    if metadata_entry['what'] == 'chart':
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

class ChartsFamily:
  def __init__(self, stats_cluster):
    self._charts_data = __cluster_to_charts_data(stats_cluster)

  def charts_data(self):
    return self._charts_data