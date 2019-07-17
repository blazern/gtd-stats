import unittest

from datetime import datetime
from core.chart.modifiers.values_sum_chart_modifier import *
from core.chart.chart_data import *

def str_to_date(date_str):
  return datetime.strptime(date_str, '%d/%m/%Y')

class ValuesSumChartModifierTest(unittest.TestCase):
  def test_sumes_values(self):
    line1 = ChartLineData('line1', [1, 2, 3], [1, 1, 1])
    line2 = ChartLineData('line2', [2, 3, 4], [1, 1, 1])
    line3 = ChartLineData('line3', [0, 1, 2], [1, 1, 1])
    ignored_line = ChartLineData('line4', [0, 1, 2], [1, 1, 1])

    expected_x_coords = [0, 1, 2, 3, 4]
    expected_y_coords = [1, 2, 3, 2, 1]
    modifier = ValuesSumChartModifier('new_line', ['line1', 'line2', 'line3'])

    converted_lines = modifier.convert_lines([line1, line2, line3, ignored_line])
    self.assertEqual(5, len(converted_lines))

    new_line = converted_lines[4]
    self.assertEqual(expected_x_coords, new_line.x_coords())
    self.assertEqual(expected_y_coords, new_line.y_coords())

  def test_constructs_from_dict(self):
    modifier_dict = {
      'what':'chart',
      'title': 'some title',
      'type': 'values-sum',
      'sumed-lines-names': ['oldline1', 'oldline2'],
      'new-line-name': 'new line'
    }
    modifier = ValuesSumChartModifier.try_create_from(modifier_dict)
    self.assertEqual('new line', modifier._new_line_name)
    self.assertEqual(['oldline1', 'oldline2'], modifier._sumed_lines_names)

  def test_doesnt_construct_from_wrong_type_in_dict(self):
    modifier_dict = {
      'what':'chart',
      'title': 'some title',
      'type': 'values sum!',
      'sumed-lines-names': ['oldline1', 'oldline2'],
      'new-line-name': 'new line'
    }
    modifier = ValuesSumChartModifier.try_create_from(modifier_dict)
    self.assertEqual(None, modifier)