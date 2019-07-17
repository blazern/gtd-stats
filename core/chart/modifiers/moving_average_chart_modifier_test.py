import unittest

from datetime import datetime
from core.chart.modifiers.moving_average_chart_modifier import *
from core.chart.chart_data import *

def str_to_date(date_str):
  return datetime.strptime(date_str, '%d/%m/%Y')

class ChartsModifiersCompositeTest(unittest.TestCase):
  def test_moving_average_modifier_works(self):
    modifier = MovingAverageChartModifier(offset = 1)
    x_coords = [str_to_date('24/05/2019'), str_to_date('25/05/2019'), str_to_date('26/05/2019')]
    y_coords = [1, 2, 3]
    expected_converted_y = [1.0, 1.5, 2.5]
    
    line = ChartLineData('', x_coords, y_coords)
    converted_lines = modifier.convert_lines([line])
    self.assertEqual(1, len(converted_lines))
    converted_x = converted_lines[0].x_coords()
    converted_y = converted_lines[0].y_coords()

    self.assertEqual(x_coords, converted_x)
    self.assertEqual(expected_converted_y, converted_y)

  def test_constructs_from_dict(self):
    modifier_dict = {
      'what': 'chart',
      'title': 'some title',
      'type': 'moving-average',
      'offset': 3
    }
    modifier = MovingAverageChartModifier.try_create_from(modifier_dict)
    self.assertEqual(3, modifier.offset)

  def test_doesnt_construct_from_wrong_type_in_dict(self):
    modifier_dict = {
      'what': 'chart',
      'title': 'some title',
      'type': 'moving average',
      'offset': 3
    }
    modifier = MovingAverageChartModifier.try_create_from(modifier_dict)
    self.assertEqual(None, modifier)