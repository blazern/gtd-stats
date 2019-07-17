from core.chart.modifiers.chart_modifier import *
from core.chart.chart_data import *

class MovingAverageChartModifier(ChartModifier):
  def __init__(self, offset):
    self.offset = offset

  @staticmethod
  def try_create_from(modifier_dict):
    if modifier_dict['type'] != 'moving-average':
      return None
    offset = modifier_dict['offset']
    return MovingAverageChartModifier(offset)

  # Override
  def convert_lines(self, lines):
    updated_lines = []
    for line in lines:
      x_coords, y_coords = self._convert_coords(line.x_coords(), line.y_coords())
      updated_lines.append(ChartLineData(line.title(), x_coords, y_coords))
    return updated_lines

  def _convert_coords(self, coords_x, coords_y):
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