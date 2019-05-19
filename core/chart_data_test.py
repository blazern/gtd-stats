import unittest

from datetime import datetime

from core.stats_cluster import StatsCluster
from core.chart_data import ChartData

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
      16/04/2019;4;vadim
      15/05/2019;1;kiril
      ''')
   
    chart_data = ChartData(cluster)
    lines = chart_data.lines()
    self.assertEqual(3, len(lines))
    
    lines_dict = lines_to_lines_dict(lines)
    self.assertTrue('danil' in lines_dict)
    self.assertTrue('kiril' in lines_dict)
    self.assertTrue('vadim' in lines_dict)

    self.assertEqual(2, len(lines_dict['danil'].x_coords()))
    self.assertEqual(2, len(lines_dict['danil'].y_coords()))
    self.assertEqual(str_to_date('17/05/2019'), lines_dict['danil'].x_coords()[0])
    self.assertEqual(str_to_date('18/05/2019'), lines_dict['danil'].x_coords()[1])
    self.assertEqual(3, lines_dict['danil'].y_coords()[0])
    self.assertEqual(1, lines_dict['danil'].y_coords()[1])

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

    self.assertEqual(1, len(lines_dict['vadim'].x_coords()))
    self.assertEqual(1, len(lines_dict['vadim'].y_coords()))
    self.assertEqual(str_to_date('16/04/2019'), lines_dict['vadim'].x_coords()[0])
    self.assertEqual(4, lines_dict['vadim'].y_coords()[0])
