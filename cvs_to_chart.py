#!/usr/bin/env python3.7

import argparse
import sys
import os
import subprocess

from plotly.offline import plot
import plotly.graph_objs as graph_objs

import core.stats.stats_file_utils as stats_file_utils
from core.stats.stats_entry import StatsEntry
from core.chart.chart_data import ChartData
from core.chart.charts_family import *

def file_to_html_chart(path):
  cluster = stats_file_utils.load_from(path)
  charts_family = ChartsFamily(cluster)
  # chart_data = ChartData(cluster)

  cvs_file_name = os.path.basename(path)
  cvs_graph_objs_dict = {}

  cvs_graph_objs = []
  for line in chart_data.lines():
    cvs_graph_objs.append(graph_objs.Scatter(x=line.x_coords(),
                                             y=line.y_coords(),
                                             name=line.title()))
  cvs_graph_objs_dict[cvs_file_name] = cvs_graph_objs

  for appearance in cluster.metadata().chart_appearances():
    cvs_graph_objs = []
    for line in chart_data.lines():
      x_coords, y_coords = appearance.convert_coords(line.x_coords(), line.y_coords())
      cvs_graph_objs.append(graph_objs.Scatter(x=x_coords,
                                               y=y_coords,
                                               name=line.title()))
    cvs_graph_objs_dict['{} {}'.format(cvs_file_name, appearance.title)] = cvs_graph_objs

  files = {}
  for key, objs in cvs_graph_objs_dict.items():
    files[key] = '/tmp/{}.html'.format(key)
    plot(objs, filename=files[key], auto_open=False)

  html_template = '''
<!DOCTYPE html>
<html>
<body>
{}
</body>
</html> 
  '''
  iframe_template = '<h1>{}</h1><br><iframe src="{}" width="100%" height="800"></iframe>'
  iframes = ''
  for title, path in files.items():
    iframes += iframe_template.format(title, path) + '\n'
  html = html_template.format(iframes)

  out_path = '/tmp/{}_all.html'.format(cvs_file_name)
  with open(out_path, 'w') as text_file:
    text_file.write(html)
  subprocess.check_call(['xdg-open', out_path])

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
