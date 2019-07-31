from core.chart.modifiers.chart_modifier import *
from core.chart.chart_data import *

class EraseZeroValuesChartModifier(ChartModifier):
  @staticmethod
  def try_create_from(modifier_dict):
    if modifier_dict['type'] != 'erase-zero-values':
      return None
    return EraseZeroValuesChartModifier()

  # Override
  def convert_lines(self, lines):
    updated_lines = []
    for line in lines:
      updated_lines.append(self._convert_line(line))
    return updated_lines

  def _convert_line(self, line):
    x_coords_result = []
    y_coords_result = []
    for indx in range(0, len(line.x_coords())):
      x = line.x_coords()[indx]
      y = line.y_coords()[indx]
      if y != 0:
        x_coords_result.append(x)
        y_coords_result.append(y)
    return ChartLineData(line.title(), x_coords_result, y_coords_result)