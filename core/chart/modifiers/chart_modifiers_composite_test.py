import unittest

from datetime import datetime

from core.chart.modifiers.chart_modifiers_composite import *
from core.chart.modifiers.moving_average_chart_modifier import *
from core.chart.modifiers.period_chart_modifier import *

def str_to_date(date_str):
  return datetime.strptime(date_str, '%d/%m/%Y')

class ChartsModifiersCompositeTest(unittest.TestCase):
  def test_empty_composite_doesnt_convert_coords(self):
    modifiers_composite = ChartModifiersComposite('title', [])
    x_coords = [str_to_date('24/05/2019'), str_to_date('25/05/2019'), str_to_date('26/05/2019')]
    y_coords = [1, 2, 3]
    converted_x, converted_y = modifiers_composite.convert_coords(x_coords, y_coords)
    self.assertEqual(x_coords, converted_x)
    self.assertEqual(y_coords, converted_y)

  def test_composite_uses_moving_average_when_has_it(self):
    modifier = MovingAverageChartModifier(offset = 1)
    modifiers_composite = ChartModifiersComposite('title', [modifier])
    x_coords = [str_to_date('24/05/2019'), str_to_date('25/05/2019'), str_to_date('26/05/2019')]
    y_coords = [1, 2, 3]
    expected_converted_y = [1.0, 1.5, 2.5]
    converted_x, converted_y = modifiers_composite.convert_coords(x_coords, y_coords)
    self.assertEqual(x_coords, converted_x)
    self.assertEqual(expected_converted_y, converted_y)

  def test_modifiers_uses_all_modifiers_when_provided1(self):
    period_modifier = PeriodChartModifier(time_unit=PeriodChartModifier.Unit.MONTH,
                                                    time_period_size=1)
    moving_average_modifier = MovingAverageChartModifier(offset = 2)
    modifiers_composite = ChartModifiersComposite('title', [period_modifier, moving_average_modifier])
    x_coords = [str_to_date('21/01/2019'),
                str_to_date('22/02/2019'),
                str_to_date('23/02/2019'),
                str_to_date('24/03/2019'),
                str_to_date('25/04/2019'),
                str_to_date('26/05/2019')]
    y_coords = [3, 6, 9, 12, 15, 18]
    expected_converted_x = ['01/2019', '02/2019', '03/2019', '04/2019', '05/2019']
    expected_converted_y = [3.0, 9.0, 10.0, 14.0, 15.0] # Without moving average would be: [3, 15, 12, 15, 18]
    converted_x, converted_y = modifiers_composite.convert_coords(x_coords, y_coords)
    self.assertEqual(expected_converted_x, converted_x)
    self.assertEqual(expected_converted_y, converted_y)

  def test_composite_uses_all_modifiers_when_provided2(self):
    period_modifier = PeriodChartModifier(time_unit=PeriodChartModifier.Unit.MONTH,
                                                    time_period_size=1)
    moving_average_modifier = MovingAverageChartModifier(offset = 2)
    # Same as test_chart_appearance_uses_all_modifiers_when_provided1, but modifiers are other way around
    modifiers_composite = ChartModifiersComposite('title', [moving_average_modifier, period_modifier])
    x_coords = [str_to_date('21/01/2019'),
                str_to_date('22/02/2019'),
                str_to_date('23/02/2019'),
                str_to_date('24/03/2019'),
                str_to_date('25/04/2019'),
                str_to_date('26/05/2019')]
    y_coords = [3, 6, 9, 12, 15, 18]
    expected_converted_x = ['01/2019', '02/2019', '03/2019', '04/2019', '05/2019']
    expected_converted_y = [3.0, 10.5, 9.0, 12.0, 15.0] # Without period modifier would be: [3.0, 4.5, 6.0, 9.0, 12.0, 15.0]
    converted_x, converted_y = modifiers_composite.convert_coords(x_coords, y_coords)
    self.assertEqual(expected_converted_x, converted_x)
    self.assertEqual(expected_converted_y, converted_y)

  def test_composite_doesnt_accept_2_modifiers_of_same_time(self):
    moving_average_modifier1 = MovingAverageChartModifier(offset = 1)
    moving_average_modifier2 = MovingAverageChartModifier(offset = 1)
    exception_caught = False
    try:
      modifiers_composite = ChartModifiersComposite('title', [moving_average_modifier1, moving_average_modifier2])
    except:
      exception_caught = True
    self.assertTrue(exception_caught)