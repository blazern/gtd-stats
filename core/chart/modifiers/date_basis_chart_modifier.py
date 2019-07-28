from enum import Enum
from core.chart.modifiers.chart_modifier import *
from core.chart.chart_data import *

class DateBasisChartModifier(ChartModifier):
  class Unit(Enum):
    DAY = 1
    MONTH = 2
    YEAR = 3

  def __init__(self, unit, day_number):
    self._unit = unit
    self._day_number = day_number

  @staticmethod
  def try_create_from(modifier_dict):
    if modifier_dict['type'] != 'date-basis':
      return None
    day_number = modifier_dict['day-n']
    unit = modifier_dict['of-unit']
    if unit == 'week':
      unit = DateBasisChartModifier.Unit.WEEK
      if day_number > 7:
        raise ValueError('Day number cannot be greater than 7 in a week')
    elif unit == 'month':
      unit = DateBasisChartModifier.Unit.MONTH
      if day_number > 7:
        raise ValueError('Day number cannot be greater than 31 in a month')
    elif unit == 'year':
      unit = DateBasisChartModifier.Unit.YEAR
      if day_number > 7:
        raise ValueError('Day number cannot be greater than 365 in a year')
    else:
      raise ValueError('Unknown time unit: {}'.format(unit))
    return DateBasisChartModifier(unit, day_number)

  # Override
  def convert_lines(self, lines):
    # TODO: raise exception if lines x's are not dates
    # TODO: find the earliest day among all lines
    # TODO: to each line add days with zero values since earliest day to line start day
    pass

  def _find_earliest_date(self, lines):
    earliest_date = None
    for line in lines