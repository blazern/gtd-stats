from core.chart.chart_appearance import *
from core.chart.chart_data import *
from core.chart.utils import extract_chart_appearances_from_stats_metadata

def _ChartsFamily__cluster_to_charts_data(stats_cluster, title_base):
  appearances = extract_chart_appearances_from_stats_metadata(stats_cluster.metadata())
  result = [ChartData(stats_cluster, None, title_base)]
  result += [ChartData(stats_cluster, appearance, title_base) for appearance in appearances]
  return result

class ChartsFamily:
  def __init__(self, stats_cluster, title_base):
    self._charts_data = __cluster_to_charts_data(stats_cluster, title_base)

  def charts_data(self):
    return list(self._charts_data)