from collections import OrderedDict
from enum import Enum
from datetime import datetime

class ChartAppearance:
  def __init__(self, title, modifiers=[]):
    types = set()
    for modifier in modifiers:
      if type(modifier) in types:
        raise ValueError('Can\' have more than 1 modifier of same types. Duplicating modifier: {}'.format(type(modifier)))
      types.add(type(modifier))
    self.title = title
    self.modifiers = modifiers

  def convert_coords(self, coords_x, coords_y):
    if len(coords_x) != len(coords_y):
      raise ValueError('Lengths of x and y coords is different: {}, {}'.format(coords_x, coords_y))
    converted_x = coords_x
    converted_y = coords_y
    for modifier in self.modifiers:
      converted_x, converted_y = modifier.convert_coords(converted_x, converted_y)
    return converted_x, converted_y

class MovingAverageChartAppearanceModifier:
  def __init__(self, offset):
    self.offset = offset

  def convert_coords(self, coords_x, coords_y):
    converted_y = []
    for indx, x in enumerate(coords_y):
      prev_y_coords = []
      aver_indx_start = max(indx-self.offset, 0)
      aver_indx_end = indx
      for aver_indx in range(aver_indx_start, aver_indx_end+1):
        prev_y_coords.append(coords_y[aver_indx])
      average = sum(prev_y_coords) / len(prev_y_coords)
      converted_y.append(average)
    return coords_x, converted_y

class PeriodChartAppearanceModifier:
  class Unit(Enum):
    DAY = 1
    MONTH = 2
    YEAR = 3

  def __init__(self, time_unit, time_period_size):
    if not isinstance(time_unit, PeriodChartAppearanceModifier.Unit):
      raise ValueError('Time unit {} was expected to have inner Unit type, but instead is {}'.format(time_unit, type(time_unit)))
    if not isinstance(time_period_size, int):
      raise ValueError('Time period {} was expected to be int, but instead is {}'.format(time_period_size, type(time_period_size)))
    if time_period_size <= 0:
      raise ValueError('Time periods <= 0 don\'t make sence. Passed period: {}'.format(time_period_size))
    self.time_unit = time_unit
    self.time_period_size = time_period_size

  def convert_coords(self, coords_x, coords_y):
    for x in coords_x:
      if not isinstance(x, datetime):
        raise ValueError('Only accepting datetime as X type, received: {}'.format(type(x)))
    
    if self.time_unit is PeriodChartAppearanceModifier.Unit.DAY:
      grouping_fun = lambda date: date.strftime('%d/%m/%Y')
    elif self.time_unit is PeriodChartAppearanceModifier.Unit.MONTH:
      grouping_fun = lambda date: date.strftime('%m/%Y')
    elif self.time_unit is PeriodChartAppearanceModifier.Unit.YEAR:
      grouping_fun = lambda date: date.strftime('%Y')
    else:
      raise ValueError('Unknown time unit: {}'.format(self.time_unit))

    grouped_values = OrderedDict()
    for i in range(0, len(coords_x)):
      x = coords_x[i]
      y = coords_y[i]
      group_id = grouping_fun(x)
      if group_id not in grouped_values:
        grouped_values[group_id] = 0
      grouped_values[group_id] += y

    converted_x = []
    converted_y = []
    collected_groups = []
    collected_groups_value = 0
    items_left = len(grouped_values)
    for key, value in grouped_values.items():
      items_left -= 1
      collected_groups.append(key)
      collected_groups_value += value
      if len(collected_groups) == self.time_period_size or items_left == 0:
        if len(collected_groups) == 1:
          converted_x.append(collected_groups[0])
        else:
          converted_x.append('{}-{}'.format(collected_groups[0], collected_groups[-1]))
        converted_y.append(collected_groups_value)
        collected_groups = []
        collected_groups_value = 0

    return converted_x, converted_y
