import unittest

from datetime import datetime
from core.chart.modifiers.period_chart_modifier import *
from core.chart.chart_data import *

def str_to_date(date_str):
  return datetime.strptime(date_str, '%d/%m/%Y')

class PeriodChartModifierTest(unittest.TestCase):
  def test_days_period_chart_modifier_works(self):
    modifier = PeriodChartModifier(time_unit=PeriodChartModifier.Unit.DAY,
                                   time_period_size=2)
    x_coords = [str_to_date('22/05/2019'),
                str_to_date('23/05/2019'),
                str_to_date('24/05/2019'),
                str_to_date('25/05/2019'),
                str_to_date('26/05/2019')]
    y_coords = [1, 2, 3, 4, 5]
    expected_converted_x = ['22/05/2019-23/05/2019',
                            '24/05/2019-25/05/2019',
                            '26/05/2019']
    expected_converted_y = [3, 7, 5]

    line = ChartLineData('', x_coords, y_coords)
    converted_lines = modifier.convert_lines([line])
    self.assertEqual(1, len(converted_lines))
    converted_x = converted_lines[0].x_coords()
    converted_y = converted_lines[0].y_coords()

    self.assertEqual(expected_converted_x, converted_x)
    self.assertEqual(expected_converted_y, converted_y)

  def test_months_period_chart_modifier_works(self):
    modifier = PeriodChartModifier(time_unit=PeriodChartModifier.Unit.MONTH,
                                   time_period_size=2)
    x_coords = [str_to_date('21/01/2019'),
                str_to_date('22/02/2019'),
                str_to_date('23/02/2019'),
                str_to_date('24/03/2019'),
                str_to_date('25/04/2019'),
                str_to_date('26/05/2019')]
    y_coords = [1, 2, 3, 4, 5, 6]
    expected_converted_x = ['01/2019-02/2019',
                            '03/2019-04/2019',
                            '05/2019']
    expected_converted_y = [6, 9, 6]

    line = ChartLineData('', x_coords, y_coords)
    converted_lines = modifier.convert_lines([line])
    self.assertEqual(1, len(converted_lines))
    converted_x = converted_lines[0].x_coords()
    converted_y = converted_lines[0].y_coords()
    
    self.assertEqual(expected_converted_x, converted_x)
    self.assertEqual(expected_converted_y, converted_y)

  def test_months_period_chart_modifier_with_single_month_size_works(self):
    modifier = PeriodChartModifier(time_unit=PeriodChartModifier.Unit.MONTH,
                                   time_period_size=1)
    x_coords = [str_to_date('21/01/2019'),
                str_to_date('22/02/2019'),
                str_to_date('23/02/2019'),
                str_to_date('24/03/2019'),
                str_to_date('25/04/2019'),
                str_to_date('26/05/2019')]
    y_coords = [1, 2, 3, 4, 5, 6]
    expected_converted_x = ['01/2019', '02/2019', '03/2019', '04/2019', '05/2019']
    expected_converted_y = [1, 5, 4, 5, 6]
    
    line = ChartLineData('', x_coords, y_coords)
    converted_lines = modifier.convert_lines([line])
    self.assertEqual(1, len(converted_lines))
    converted_x = converted_lines[0].x_coords()
    converted_y = converted_lines[0].y_coords()

    self.assertEqual(expected_converted_x, converted_x)
    self.assertEqual(expected_converted_y, converted_y)

  def test_years_period_chart_modifier_works(self):
    modifier = PeriodChartModifier(time_unit=PeriodChartModifier.Unit.YEAR,
                                   time_period_size=2)
    x_coords = [str_to_date('21/01/2017'),
                str_to_date('22/02/2017'),
                str_to_date('23/02/2018'),
                str_to_date('24/03/2018'),
                str_to_date('25/04/2018'),
                str_to_date('26/05/2019')]
    y_coords = [1, 2, 3, 4, 5, 6]
    expected_converted_x = ['2017-2018', '2019']
    expected_converted_y = [15, 6]
    
    line = ChartLineData('', x_coords, y_coords)
    converted_lines = modifier.convert_lines([line])
    self.assertEqual(1, len(converted_lines))
    converted_x = converted_lines[0].x_coords()
    converted_y = converted_lines[0].y_coords()
    
    self.assertEqual(expected_converted_x, converted_x)
    self.assertEqual(expected_converted_y, converted_y)

  def test_constructs_from_dict(self):
    modifier_dict = {
      'what':'chart',
      'title': 'some title',
      'type': 'period',
      'unit': 'months',
      'unit-value': 123
    }
    modifier = PeriodChartModifier.try_create_from(modifier_dict)
    self.assertEqual(123, modifier.time_period_size)
    self.assertEqual(PeriodChartModifier.Unit.MONTH, modifier.time_unit)

  def test_doesnt_construct_from_wrong_type_in_dict(self):
    modifier_dict = {
      'what':'chart',
      'title': 'some title',
      'type': 'periodic stuff',
      'unit': 'months',
      'unit-value': 123
    }
    modifier = PeriodChartModifier.try_create_from(modifier_dict)
    self.assertEqual(None, modifier)