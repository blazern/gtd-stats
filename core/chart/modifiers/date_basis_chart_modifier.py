from enum import Enum
from datetime import timedelta
from datetime import datetime

from core.chart.modifiers.chart_modifier import *
from core.chart.chart_data import *

class DateBasisChartModifier(ChartModifier):
  class Unit(Enum):
    WEEK = 1
    MONTH = 2
    YEAR = 3

  def __init__(self, unit, needed_basis_day_number):
    self._unit = unit
    self._needed_basis_day_number = needed_basis_day_number

  @staticmethod
  def try_create_from(modifier_dict):
    if modifier_dict['type'] != 'date-basis':
      return None
    needed_basis_day_number = modifier_dict['day-n']
    unit = modifier_dict['of-unit']
    if unit == 'week':
      unit = DateBasisChartModifier.Unit.WEEK
      if needed_basis_day_number > 7:
        raise ValueError('Day number cannot be greater than 7 in a week')
    elif unit == 'month':
      unit = DateBasisChartModifier.Unit.MONTH
      if needed_basis_day_number > 28:
        raise ValueError('Day number cannot be greater than 28 in a month')
    elif unit == 'year':
      unit = DateBasisChartModifier.Unit.YEAR
      if needed_basis_day_number > 7:
        raise ValueError('Day number cannot be greater than 365 in a year')
    else:
      raise ValueError('Unknown time unit: {}'.format(unit))
    return DateBasisChartModifier(unit, needed_basis_day_number)

  # Override
  def convert_lines(self, lines):
    for line in lines:
      for x in line.x_coords():
        if not isinstance(x, datetime):
          raise ValueError('X must have datetime type but has: {}'.format(type(x)))

    earliest_date = self._find_earliest_date(lines)
    initial_basis_day_number = self._get_day_number_of_date(earliest_date)

    basis_day_number = initial_basis_day_number
    basis_day = earliest_date
    while basis_day_number != self._needed_basis_day_number:
      basis_day = basis_day - timedelta(days=1)
      basis_day_number = self._get_day_number_of_date(basis_day)

    updated_lines = []
    for line in lines:
      updated_lines.append(self._convert_line(line, basis_day))
    return updated_lines

  def _find_earliest_date(self, lines):
    earliest_date = None
    for line in lines:
      for x in line.x_coords():
        if earliest_date is None or x < earliest_date:
          earliest_date = x
    return earliest_date

  def _get_day_number_of_date(self, date):
    if self._unit == DateBasisChartModifier.Unit.WEEK:
      return date.weekday() + 1
    elif self._unit == DateBasisChartModifier.Unit.MONTH:
      return date.day
    elif self._unit == DateBasisChartModifier.Unit.YEAR:
      return date.timetuple().tm_yday
    else:
      raise ValueError('Unhandled time unit: {}'.format(self._unit))

  def _convert_line(self, line, basis_day):
    days_diff = (line.x_coords()[0] - basis_day).days
    x_coords_extra = []
    y_coords_extra = []
    for day_index in range(0, days_diff):
      mid_date = basis_day + timedelta(days=day_index)
      x_coords_extra.append(mid_date)
      y_coords_extra.append(0)

    return ChartLineData(line.title(), x_coords_extra + line.x_coords(), y_coords_extra + line.y_coords())