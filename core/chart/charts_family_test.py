import unittest

from core.stats.stats_metadata import *
from core.stats.stats_cluster import *
from core.chart.chart_appearance import *
from core.chart.charts_family import *

class ChartFamilyTests(unittest.TestCase):
  def setUp(self):
    self.maxDiff = None

  def test_convert_simple_stats_cluster(self):
    cluster_str = \
'''
date;id;value
14/07/2019;danil;123
14/07/2019;grisha;321
'''
    cluster = StatsCluster.from_str(cluster_str)
    charts_family = ChartsFamily(cluster, title_base='')

    charts_data = charts_family.charts_data()
    self.assertEqual(1, len(charts_data))

    chart_data = charts_data[0]
    self.assertEqual(2, len(chart_data.lines()))
    self.assertEqual(1, len(chart_data.lines()[0].x_coords()))
    self.assertEqual(1, len(chart_data.lines()[0].y_coords()))
    self.assertEqual(1, len(chart_data.lines()[1].x_coords()))
    self.assertEqual(1, len(chart_data.lines()[1].y_coords()))

  def test_has_chart_data_for_each_appearance(self):
    cluster_str = \
'''
14/07/2019;123;danil;some comment
14/07/2019;321;grisha;another comment
===
- what: chart
  type: moving-average
  title: ma
  offset: 20
- what: chart
  title: periodic
  type: period
  unit: days
  unit-value: 7
- what: format
  value: date;value;id;comment
===
'''
    cluster = StatsCluster.from_str(cluster_str)
    charts_family = ChartsFamily(cluster, title_base='')

    charts_data = charts_family.charts_data()
    # 1 chart data for original data without modifications,
    # and 1 for each appearnces (there're 2 appearances in metadata)
    self.assertEqual(3, len(charts_data))