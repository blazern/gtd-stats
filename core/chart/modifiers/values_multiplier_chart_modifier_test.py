import unittest

from datetime import datetime
from core.chart.modifiers.values_multiplier_chart_modifier import *
from core.chart.chart_data import *

def str_to_date(date_str):
  return datetime.strptime(date_str, '%d/%m/%Y')

class ValuesMultiplierChartModifierTest(unittest.TestCase):
  def test_multiplies_values(self):
    line = ChartLineData('', [1, 2, 3], [1, 2, 3])

    expected_x_coords = [1, 2, 3]
    expected_y_coords = [2, 4, 6]
    modifier = ValuesMultiplierChartModifier(2)

    converted_lines = modifier.convert_lines([line])
    self.assertEqual(1, len(converted_lines))

    converted_line = converted_lines[0]
    self.assertEqual(expected_x_coords, converted_line.x_coords())
    self.assertEqual(expected_y_coords, converted_line.y_coords())

  def test_constructs_from_dict(self):
    modifier_dict = {
      'what':'chart',
      'title': 'some title',
      'type': 'values-multiplier',
      'factor': 2
    }
    modifier = ValuesMultiplierChartModifier.try_create_from(modifier_dict)
    self.assertEqual(2, modifier._factor)

  def test_doesnt_construct_from_wrong_type_in_dict(self):
    modifier_dict = {
      'what':'chart',
      'title': 'some title',
      'type': 'values multiplier',
      'factor': 2
    }
    modifier = ValuesMultiplierChartModifier.try_create_from(modifier_dict)
    self.assertEqual(None, modifier)