from core.chart.modifiers.chart_modifier import *
from core.chart.chart_data import *

class ValuesSumChartModifier(ChartModifier):
  def __init__(self, new_line_name, sumed_lines_names):
    self._new_line_name = new_line_name
    self._sumed_lines_names = sumed_lines_names

  @staticmethod
  def try_create_from(modifier_dict):
    if modifier_dict['type'] != 'values-sum':
      return None
    sumed_lines_names = modifier_dict['sumed-lines-names']
    new_line_name = modifier_dict['new-line-name']
    if not isinstance(sumed_lines_names, list):
      raise ValueError('Values names expected to be a list: {}'.format(modifier_dict))
    if len(sumed_lines_names) == 0:
      raise ValueError('Empty sum not supported: {}'.format(modifier_dict))
    return ValuesSumChartModifier(new_line_name, sumed_lines_names)

  # Override
  def multiple_modifiers_of_type_allowed(self):
    return True

  # Override
  def convert_lines(self, lines):
    needed_lines = []
    for line in lines:
      if line.title() in self._sumed_lines_names:
        needed_lines.append(line)

    if len(needed_lines) != len(self._sumed_lines_names):
      found_names = [line.title() for line in needed_lines]
      all_names = [line.title() for line in lines]
      raise ValueError('Found line names ({}) and expected names ({}) differ. All names: {}'.format(
        found_names, self._sumed_lines_names, all_names))

    x_to_all_y_sum_dict = {}
    for line in needed_lines:
      for indx in range(0, len(line.x_coords())):
        x = line.x_coords()[indx]
        y = line.y_coords()[indx]
        if x not in x_to_all_y_sum_dict:
          x_to_all_y_sum_dict[x] = 0
        x_to_all_y_sum_dict[x] += y

    x_and_y_coords = [(x, x_to_all_y_sum_dict[x]) for x in sorted(x_to_all_y_sum_dict)]
    x_coords = [x for x, y in x_and_y_coords]
    y_coords = [y for x, y in x_and_y_coords]
    new_line = ChartLineData(self._new_line_name, x_coords, y_coords)

    return lines + [new_line]
