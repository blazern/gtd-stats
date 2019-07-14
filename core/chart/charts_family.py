from core.chart.modifiers.chart_modifiers_composite import *
from core.chart.chart_data import *
from core.chart.utils import extract_chart_modifiers_from_stats_metadata

def _ChartsFamily__cluster_to_charts_data(stats_cluster, title_base):
  modifiers = extract_chart_modifiers_from_stats_metadata(stats_cluster.metadata())
  result = [ChartData(stats_cluster, None, title_base)]
  result += [ChartData(stats_cluster, modifier, title_base) for modifier in modifiers]
  return result

class ChartsFamily:
  def __init__(self, stats_cluster, title_base):
    self._charts_data = __cluster_to_charts_data(stats_cluster, title_base)

  def charts_data(self):
    return list(self._charts_data)