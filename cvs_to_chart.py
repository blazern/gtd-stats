#!/usr/bin/env python3.7

import argparse
import sys

from plotly.offline import plot
import plotly.graph_objs as graph_objs

import core.stats_file_utils as stats_file_utils
from core.stats_entry import StatsEntry
from core.chart_data import ChartData

def file_to_html_chart(path):
  cluster = stats_file_utils.load_from(path)
  chart_data = ChartData(cluster)
  cvs_graph_objs = []
  for line in chart_data.lines():
    cvs_graph_objs.append(graph_objs.Scatter(x=line.x_coords(),
                                             y=line.y_coords(),
                                             name=line.title()))

  html = plot(cvs_graph_objs, filename='/tmp/my-graph.html')#output_type='div')

def stats_entries_to_graph_objs(stats_entries):
  separated_stats = {}
  for entry in stats_entries:
    if entry.description not in separated_stats:
      separated_stats[entry.description] = []
    separated_stats[entry.description].append(entry)

  result = []
  for descr, stats in separated_stats.items():
    x, y = stats_entries_to_x_y_data(stats)
    result.append(graph_objs.Scatter(x=x, y=y, name=descr))
  return result

def main(argv):
  parser = argparse.ArgumentParser(description='Transforms given cvs files into html charts')
  parser.add_argument('--cvs', required=True,
                      help='Paths to cvs file which will be transformed into chart')
  options = parser.parse_args()
  file_to_html_chart(options.cvs)

if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
