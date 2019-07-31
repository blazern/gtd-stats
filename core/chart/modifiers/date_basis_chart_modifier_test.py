import unittest

from datetime import datetime
from core.chart.modifiers.date_basis_chart_modifier import *
from core.chart.chart_data import *

def str_to_date(date_str):
  return datetime.strptime(date_str, '%d/%m/%Y')

class DateBasisChartModifierTest(unittest.TestCase):
  def test_chooses_correct_week_date_basis(self):
    lines = [ChartLineData('l1', [str_to_date('30/07/2019'), str_to_date('31/07/2019')], [1, 2]),
             ChartLineData('l2', [str_to_date('31/07/2019'), str_to_date('01/08/2019')], [2, 3])]

    modifier = DateBasisChartModifier(DateBasisChartModifier.Unit.WEEK, 1)
    expected_x_coords1 = [str_to_date('29/07/2019'),
                          str_to_date('30/07/2019'),
                          str_to_date('31/07/2019')]
    expected_y_coords1 = [0, 1, 2]
    expected_x_coords2 = [str_to_date('29/07/2019'),
                          str_to_date('30/07/2019'),
                          str_to_date('31/07/2019'),
                          str_to_date('01/08/2019')]
    expected_y_coords2 = [0, 0, 2, 3]

    converted_lines = modifier.convert_lines(lines)
    self.assertEqual(2, len(converted_lines))

    self.assertEqual(expected_x_coords1, converted_lines[0].x_coords())
    self.assertEqual(expected_y_coords1, converted_lines[0].y_coords())
    self.assertEqual(expected_x_coords2, converted_lines[1].x_coords())
    self.assertEqual(expected_y_coords2, converted_lines[1].y_coords())

  def test_chooses_correct_month_date_basis(self):
    lines = [ChartLineData('l1', [str_to_date('04/07/2019'), str_to_date('05/07/2019')], [1, 2]),
             ChartLineData('l2', [str_to_date('05/07/2019'), str_to_date('10/07/2019')], [2, 3])]

    modifier = DateBasisChartModifier(DateBasisChartModifier.Unit.MONTH, 2)
    expected_x_coords1 = [str_to_date('02/07/2019'),
                          str_to_date('03/07/2019'),
                          str_to_date('04/07/2019'),
                          str_to_date('05/07/2019')]
    expected_y_coords1 = [0, 0, 1, 2]
    expected_x_coords2 = [str_to_date('02/07/2019'),
                          str_to_date('03/07/2019'),
                          str_to_date('04/07/2019'),
                          str_to_date('05/07/2019'),
                          str_to_date('10/07/2019')]
    expected_y_coords2 = [0, 0, 0, 2, 3]

    converted_lines = modifier.convert_lines(lines)
    self.assertEqual(2, len(converted_lines))

    self.assertEqual(expected_x_coords1, converted_lines[0].x_coords())
    self.assertEqual(expected_y_coords1, converted_lines[0].y_coords())
    self.assertEqual(expected_x_coords2, converted_lines[1].x_coords())
    self.assertEqual(expected_y_coords2, converted_lines[1].y_coords())

  def test_chooses_correct_year_date_basis(self):
    lines = [ChartLineData('l1', [str_to_date('02/01/2019')], [1]),
             ChartLineData('l2', [str_to_date('05/01/2019'), str_to_date('10/01/2019')], [2, 3])]

    modifier = DateBasisChartModifier(DateBasisChartModifier.Unit.YEAR, 1)
    expected_x_coords1 = [str_to_date('01/01/2019'),
                          str_to_date('02/01/2019')]
    expected_y_coords1 = [0, 1]
    expected_x_coords2 = [str_to_date('01/01/2019'),
                          str_to_date('02/01/2019'),
                          str_to_date('03/01/2019'),
                          str_to_date('04/01/2019'),
                          str_to_date('05/01/2019'),
                          str_to_date('10/01/2019')]
    expected_y_coords2 = [0, 0, 0, 0, 2, 3]

    converted_lines = modifier.convert_lines(lines)
    self.assertEqual(2, len(converted_lines))

    self.assertEqual(expected_x_coords1, converted_lines[0].x_coords())
    self.assertEqual(expected_y_coords1, converted_lines[0].y_coords())
    self.assertEqual(expected_x_coords2, converted_lines[1].x_coords())
    self.assertEqual(expected_y_coords2, converted_lines[1].y_coords())

  def test_doesnt_change_date_basis_if_lines_already_on_it(self):
    lines = [ChartLineData('l1', [str_to_date('29/07/2019'), str_to_date('31/07/2019')], [1, 2]),
             ChartLineData('l2', [str_to_date('31/07/2019'), str_to_date('01/08/2019')], [2, 3])]

    modifier = DateBasisChartModifier(DateBasisChartModifier.Unit.WEEK, 1)
    expected_x_coords1 = [str_to_date('29/07/2019'),
                          str_to_date('31/07/2019')]
    expected_y_coords1 = [1, 2]
    expected_x_coords2 = [str_to_date('29/07/2019'),
                          str_to_date('30/07/2019'),
                          str_to_date('31/07/2019'),
                          str_to_date('01/08/2019')]
    expected_y_coords2 = [0, 0, 2, 3]

    converted_lines = modifier.convert_lines(lines)
    self.assertEqual(2, len(converted_lines))

    self.assertEqual(expected_x_coords1, converted_lines[0].x_coords())
    self.assertEqual(expected_y_coords1, converted_lines[0].y_coords())
    self.assertEqual(expected_x_coords2, converted_lines[1].x_coords())
    self.assertEqual(expected_y_coords2, converted_lines[1].y_coords())

  def test_chooses_correct_date_basis_if_one_of_lines_already_on_it_and_another_is_earlier(self):
    # l1 - already on monday
    # l2 - on tuesday of the week before
    lines = [ChartLineData('l1', [str_to_date('29/07/2019'), str_to_date('31/07/2019')], [1, 2]),
             ChartLineData('l2', [str_to_date('23/07/2019')], [2])]

    modifier = DateBasisChartModifier(DateBasisChartModifier.Unit.WEEK, 1)
    expected_x_coords1 = [str_to_date('22/07/2019'),
                          str_to_date('23/07/2019'),
                          str_to_date('24/07/2019'),
                          str_to_date('25/07/2019'),
                          str_to_date('26/07/2019'),
                          str_to_date('27/07/2019'),
                          str_to_date('28/07/2019'),
                          str_to_date('29/07/2019'),
                          str_to_date('31/07/2019')]
    expected_y_coords1 = [0, 0, 0, 0, 0, 0, 0, 1, 2]
    expected_x_coords2 = [str_to_date('22/07/2019'),
                          str_to_date('23/07/2019')]
    expected_y_coords2 = [0, 2]

    converted_lines = modifier.convert_lines(lines)
    self.assertEqual(2, len(converted_lines))

    self.assertEqual(expected_x_coords1, converted_lines[0].x_coords())
    self.assertEqual(expected_y_coords1, converted_lines[0].y_coords())
    self.assertEqual(expected_x_coords2, converted_lines[1].x_coords())
    self.assertEqual(expected_y_coords2, converted_lines[1].y_coords())

  def test_constructs_from_dict(self):
    modifier_dict = {
      'what':'chart',
      'title': 'some title',
      'type': 'date-basis',
      'day-n': 3,
      'of-unit': 'week'
    }
    modifier = DateBasisChartModifier.try_create_from(modifier_dict)
    self.assertEqual(3, modifier._needed_basis_day_number)
    self.assertEqual(DateBasisChartModifier.Unit.WEEK, modifier._unit)

  def test_doesnt_construct_from_wrong_type_in_dict(self):
    modifier_dict = {
      'what':'chart',
      'title': 'some title',
      'type': 'date basis',
      'day-n': 3,
      'of-unit': 'week'
    }
    modifier = DateBasisChartModifier.try_create_from(modifier_dict)
    self.assertEqual(None, modifier)