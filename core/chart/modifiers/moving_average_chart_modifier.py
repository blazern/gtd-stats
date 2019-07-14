from core.chart.modifiers.chart_modifier import *

class MovingAverageChartModifier(ChartModifier):
  def __init__(self, offset):
    self.offset = offset

  # Override
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