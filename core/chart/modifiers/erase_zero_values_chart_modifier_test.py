import unittest

from datetime import datetime
from core.chart.modifiers.erase_zero_values_chart_modifier import *
from core.chart.chart_data import *

def str_to_date(date_str):
  return datetime.strptime(date_str, '%d/%m/%Y')

class EraseZeroValuesChartModifierTest(unittest.TestCase):
  def test_erases_zeros(self):
    lines = [ChartLineData('l1', [1, 2, 3], [11, 0, 33]),
             ChartLineData('l2', [1, 2, 3], [0, 22, 33]),
             ChartLineData('l3', [1, 2, 3], [11, 22, 0])]

    expected_x_coords1 = [1, 3]
    expected_y_coords1 = [11, 33]
    expected_x_coords2 = [2, 3]
    expected_y_coords2 = [22, 33]
    expected_x_coords3 = [1, 2]
    expected_y_coords3 = [11, 22]
    modifier = EraseZeroValuesChartModifier()

    converted_lines = modifier.convert_lines(lines)
    self.assertEqual(3, len(converted_lines))

    self.assertEqual(expected_x_coords1, converted_lines[0].x_coords())
    self.assertEqual(expected_y_coords1, converted_lines[0].y_coords())
    self.assertEqual(expected_x_coords2, converted_lines[1].x_coords())
    self.assertEqual(expected_y_coords2, converted_lines[1].y_coords())
    self.assertEqual(expected_x_coords3, converted_lines[2].x_coords())
    self.assertEqual(expected_y_coords3, converted_lines[2].y_coords())

  def test_constructs_from_dict(self):
    modifier_dict = {
      'what':'chart',
      'title': 'some title',
      'type': 'erase-zero-values'
    }
    modifier = EraseZeroValuesChartModifier.try_create_from(modifier_dict)
    self.assertNotEqual(None, modifier)

  def test_doesnt_construct_from_wrong_type_in_dict(self):
    modifier_dict = {
      'what':'chart',
      'title': 'some title',
      'type': 'erase zero values'
    }
    modifier = EraseZeroValuesChartModifier.try_create_from(modifier_dict)
    self.assertEqual(None, modifier)