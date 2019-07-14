import unittest

from datetime import datetime
from core.chart.modifiers.moving_average_chart_modifier import *

def str_to_date(date_str):
  return datetime.strptime(date_str, '%d/%m/%Y')

class ChartsModifiersCompositeTest(unittest.TestCase):
  def test_moving_average_modifier_works(self):
    modifier = MovingAverageChartModifier(offset = 1)
    x_coords = [str_to_date('24/05/2019'), str_to_date('25/05/2019'), str_to_date('26/05/2019')]
    y_coords = [1, 2, 3]
    expected_converted_y = [1.0, 1.5, 2.5]
    converted_x, converted_y = modifier.convert_coords(x_coords, y_coords)
    self.assertEqual(x_coords, converted_x)
    self.assertEqual(expected_converted_y, converted_y)