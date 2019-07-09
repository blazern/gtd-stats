import unittest

from datetime import datetime

from core.stats.stats_cluster import StatsCluster
from core.chart.chart_data import ChartData

def lines_to_lines_dict(lines):
  lines_dict = {}
  for line in lines:
    if line.title() in lines_dict:
      raise ValueError('Line\'s title {} is not unique'.format(line.title()))
    lines_dict[line.title()] = line
  return lines_dict

def str_to_date(string):
  return datetime.strptime(string, '%d/%m/%Y')

class ChartDataTest(unittest.TestCase):
  def test_can_transform_stats_cluster_to_chart_data(self):
    cluster = StatsCluster.from_str('''
      date;value;id
      18/05/2019;1;danil
      18/05/2019;2;kiril
      17/05/2019;3;danil
      16/05/2019;4;vadim
      15/05/2019;1;kiril
      ''')
   
    chart_data = ChartData(cluster)
    lines = chart_data.lines()
    self.assertEqual(3, len(lines))
    
    lines_dict = lines_to_lines_dict(lines)
    self.assertTrue('danil' in lines_dict)
    self.assertTrue('kiril' in lines_dict)
    self.assertTrue('vadim' in lines_dict)

    # Note that there're 4 coords, not 4, because all lines start at the earliest date
    self.assertEqual(4, len(lines_dict['danil'].x_coords()))
    self.assertEqual(4, len(lines_dict['danil'].y_coords()))
    self.assertEqual(str_to_date('15/05/2019'), lines_dict['danil'].x_coords()[0])
    self.assertEqual(str_to_date('16/05/2019'), lines_dict['danil'].x_coords()[1])
    self.assertEqual(str_to_date('17/05/2019'), lines_dict['danil'].x_coords()[2])
    self.assertEqual(str_to_date('18/05/2019'), lines_dict['danil'].x_coords()[3])
    self.assertEqual(0, lines_dict['danil'].y_coords()[0])
    self.assertEqual(0, lines_dict['danil'].y_coords()[1])
    self.assertEqual(3, lines_dict['danil'].y_coords()[2])
    self.assertEqual(1, lines_dict['danil'].y_coords()[3])

    self.assertEqual(4, len(lines_dict['kiril'].x_coords()))
    self.assertEqual(4, len(lines_dict['kiril'].y_coords()))
    self.assertEqual(str_to_date('15/05/2019'), lines_dict['kiril'].x_coords()[0])
    self.assertEqual(str_to_date('16/05/2019'), lines_dict['kiril'].x_coords()[1])
    self.assertEqual(str_to_date('17/05/2019'), lines_dict['kiril'].x_coords()[2])
    self.assertEqual(str_to_date('18/05/2019'), lines_dict['kiril'].x_coords()[3])
    self.assertEqual(1, lines_dict['kiril'].y_coords()[0])
    self.assertEqual(0, lines_dict['kiril'].y_coords()[1])
    self.assertEqual(0, lines_dict['kiril'].y_coords()[2])
    self.assertEqual(2, lines_dict['kiril'].y_coords()[3])

    # Note that there're 2 coords, not 1, because all lines start at the earliest date
    self.assertEqual(2, len(lines_dict['vadim'].x_coords()))
    self.assertEqual(2, len(lines_dict['vadim'].y_coords()))
    self.assertEqual(str_to_date('15/05/2019'), lines_dict['vadim'].x_coords()[0])
    self.assertEqual(str_to_date('16/05/2019'), lines_dict['vadim'].x_coords()[1])
    self.assertEqual(0, lines_dict['vadim'].y_coords()[0])
    self.assertEqual(4, lines_dict['vadim'].y_coords()[1])

  def test_can_transform_stats_cluster_with_multiple_values_to_chart_data(self):
    cluster = StatsCluster.from_str('''
      date;value:valuename1;value:valuename2
      18/05/2019;1;10
      15/05/2019;2;20
      ''')
   
    chart_data = ChartData(cluster)
    lines = chart_data.lines()
    self.assertEqual(2, len(lines))
    
    lines_dict = lines_to_lines_dict(lines)
    self.assertTrue('valuename1' in lines_dict)
    self.assertTrue('valuename2' in lines_dict)

    self.assertEqual(4, len(lines_dict['valuename1'].x_coords()))
    self.assertEqual(4, len(lines_dict['valuename1'].y_coords()))
    self.assertEqual(str_to_date('15/05/2019'), lines_dict['valuename1'].x_coords()[0])
    self.assertEqual(str_to_date('16/05/2019'), lines_dict['valuename1'].x_coords()[1])
    self.assertEqual(str_to_date('17/05/2019'), lines_dict['valuename1'].x_coords()[2])
    self.assertEqual(str_to_date('18/05/2019'), lines_dict['valuename1'].x_coords()[3])
    self.assertEqual(2, lines_dict['valuename1'].y_coords()[0])
    self.assertEqual(0, lines_dict['valuename1'].y_coords()[1])
    self.assertEqual(0, lines_dict['valuename1'].y_coords()[2])
    self.assertEqual(1, lines_dict['valuename1'].y_coords()[3])

    self.assertEqual(4, len(lines_dict['valuename2'].x_coords()))
    self.assertEqual(4, len(lines_dict['valuename2'].y_coords()))
    self.assertEqual(str_to_date('15/05/2019'), lines_dict['valuename2'].x_coords()[0])
    self.assertEqual(str_to_date('16/05/2019'), lines_dict['valuename2'].x_coords()[1])
    self.assertEqual(str_to_date('17/05/2019'), lines_dict['valuename2'].x_coords()[2])
    self.assertEqual(str_to_date('18/05/2019'), lines_dict['valuename2'].x_coords()[3])
    self.assertEqual(20, lines_dict['valuename2'].y_coords()[0])
    self.assertEqual(0, lines_dict['valuename2'].y_coords()[1])
    self.assertEqual(0, lines_dict['valuename2'].y_coords()[2])
    self.assertEqual(10, lines_dict['valuename2'].y_coords()[3])

  def test_can_transform_stats_cluster_with_multiple_values_and_ids_to_chart_data(self):
    cluster = StatsCluster.from_str('''
      date;value:valuename1;value:valuename2;id
      18/05/2019;1;10;danil
      17/05/2019;2;20;kiril
      16/05/2019;3;30;danil
      ''')
   
    chart_data = ChartData(cluster)
    lines = chart_data.lines()
    self.assertEqual(4, len(lines))
    
    lines_dict = lines_to_lines_dict(lines)
    self.assertTrue('danil_valuename1' in lines_dict)
    self.assertTrue('danil_valuename2' in lines_dict)
    self.assertTrue('kiril_valuename1' in lines_dict)
    self.assertTrue('kiril_valuename2' in lines_dict)

    self.assertEqual(3, len(lines_dict['danil_valuename1'].x_coords()))
    self.assertEqual(3, len(lines_dict['danil_valuename1'].y_coords()))
    self.assertEqual(str_to_date('16/05/2019'), lines_dict['danil_valuename1'].x_coords()[0])
    self.assertEqual(str_to_date('17/05/2019'), lines_dict['danil_valuename1'].x_coords()[1])
    self.assertEqual(str_to_date('18/05/2019'), lines_dict['danil_valuename1'].x_coords()[2])
    self.assertEqual(3, lines_dict['danil_valuename1'].y_coords()[0])
    self.assertEqual(0, lines_dict['danil_valuename1'].y_coords()[1])
    self.assertEqual(1, lines_dict['danil_valuename1'].y_coords()[2])

    self.assertEqual(3, len(lines_dict['danil_valuename2'].x_coords()))
    self.assertEqual(3, len(lines_dict['danil_valuename2'].y_coords()))
    self.assertEqual(str_to_date('16/05/2019'), lines_dict['danil_valuename2'].x_coords()[0])
    self.assertEqual(str_to_date('17/05/2019'), lines_dict['danil_valuename2'].x_coords()[1])
    self.assertEqual(str_to_date('18/05/2019'), lines_dict['danil_valuename2'].x_coords()[2])
    self.assertEqual(30, lines_dict['danil_valuename2'].y_coords()[0])
    self.assertEqual(0, lines_dict['danil_valuename2'].y_coords()[1])
    self.assertEqual(10, lines_dict['danil_valuename2'].y_coords()[2])

    # Note that there're 2 coords, not 1, because all lines start at the earliest date
    self.assertEqual(2, len(lines_dict['kiril_valuename1'].x_coords()))
    self.assertEqual(2, len(lines_dict['kiril_valuename1'].y_coords()))
    self.assertEqual(str_to_date('16/05/2019'), lines_dict['kiril_valuename1'].x_coords()[0])
    self.assertEqual(str_to_date('17/05/2019'), lines_dict['kiril_valuename1'].x_coords()[1])
    self.assertEqual(0, lines_dict['kiril_valuename1'].y_coords()[0])
    self.assertEqual(2, lines_dict['kiril_valuename1'].y_coords()[1])

    self.assertEqual(2, len(lines_dict['kiril_valuename2'].x_coords()))
    self.assertEqual(2, len(lines_dict['kiril_valuename2'].y_coords()))
    self.assertEqual(str_to_date('16/05/2019'), lines_dict['kiril_valuename2'].x_coords()[0])
    self.assertEqual(str_to_date('17/05/2019'), lines_dict['kiril_valuename2'].x_coords()[1])
    self.assertEqual(0, lines_dict['kiril_valuename2'].y_coords()[0])
    self.assertEqual(20, lines_dict['kiril_valuename2'].y_coords()[1])
