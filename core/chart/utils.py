from core.chart.modifiers.chart_modifiers_composite import *
from core.chart.modifiers.moving_average_chart_modifier import *
from core.chart.modifiers.period_chart_modifier import *

def extract_chart_modifiers_from_stats_metadata(metadata):
  modifiers_fabrics = [
    lambda metadata_dict: MovingAverageChartModifier.try_create_from(metadata_dict),
    lambda metadata_dict: PeriodChartModifier.try_create_from(metadata_dict)
  ]

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
        modifier = None
        for modifier_fabric in modifiers_fabrics:
          modifier = modifier_fabric(modifier_dict)
          if modifier is not None:
            break
        if modifier is None:
          raise ValueError('Couldn\'t find a modifier fabric to instantiate {}'.format(modifier_dict))
        submodifiers.append(modifier)

      modifiers.append(ChartModifiersComposite(title, submodifiers))
  return modifiers