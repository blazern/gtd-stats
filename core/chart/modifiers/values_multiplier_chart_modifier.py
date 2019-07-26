from core.chart.modifiers.chart_modifier import *
from core.chart.chart_data import *

class ValuesMultiplierChartModifier(ChartModifier):
  def __init__(self, factor):
    self._factor = factor

  @staticmethod
  def try_create_from(modifier_dict):
    if modifier_dict['type'] != 'values-multiplier':
      return None
    factor = modifier_dict['factor']
    return ValuesMultiplierChartModifier(factor)

  # Override
  def convert_lines(self, lines):
    updated_lines = []
    for line in lines:
      x_coords, y_coords = self._convert_coords(line.x_coords(), line.y_coords())
      updated_lines.append(ChartLineData(line.title(), x_coords, y_coords))
    return updated_lines

  def _convert_coords(self, x_coords, y_coords):
    y_coords_updated = []
    for y in y_coords:
      y_coords_updated.append(y * self._factor)
    return x_coords, y_coords_updated