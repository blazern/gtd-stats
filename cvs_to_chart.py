#!/usr/bin/env python3.7

# todo:
# read cvs file,
# convert to stats entries,
# insert not existing elements between existing ones,
# build the chart div

import argparse
import sys

from plotly.offline import plot
import plotly.graph_objs as graph_objs

import core.stats_file_utils
from core.stats_entry import StatsEntry

def file_to_html_chart(path):
  stats = stats_file_utils.load_from(options.extra_input_file)
  x = []
  y = []
  prev_date = None
  for stats_entry in stats:
    if prev_date is None:
      curr_date = stats_entry.date
      val = stats_entry.value
    elif stats_entry.date.minus_days(1) == prev_date:
      curr_date = 
    x.append(curr_date)
    y.append(val)

    prev_date = 
  html = plot([go.Scatter(x=[1, 2, 3], y=[3, 2, 6])], output_type='div')

def main(argv):
  parser = argparse.ArgumentParser(description='Transforms given cvs files into html charts')
  parser.add_argument('--cvs', required=True, nargs='*',
                      help='List of paths to cvs files which will be transformed into charts')
  parser.add_argument('--out-file', help='Optional path to an output file to be used instead of stdout')
  options = parser.parse_args()

if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))


# from plotly.offline import plot
# import plotly.graph_objs as go

# plot([go.Scatter(x=[1, 2, 3], y=[3, 2, 6])], filename='my-graph.html')
# # We can also download an image of the plot by setting the image parameter
# # to the image format we want
# plot([go.Scatter(x=[1, 2, 3], y=[3, 2, 6])], filename='my-graph.html'
#      image='jpeg')
# ```
# More examples below.

# figure_or_data -- a plotly.graph_objs.Figure or plotly.graph_objs.Data or
#                   dict or list that describes a Plotly graph.
#                   See https://plot.ly/python/ for examples of
#                   graph descriptions.

# Keyword arguments:
# show_link (default=False) -- display a link in the bottom-right corner of
#     of the chart that will export the chart to Plotly Cloud or
#     Plotly Enterprise
# link_text (default='Export to plot.ly') -- the text of export link
# validate (default=True) -- validate that all of the keys in the figure
#     are valid? omit if your version of plotly.js has become outdated
#     with your version of graph_reference.json or if you need to include
#     extra, unnecessary keys in your figure.
# output_type ('file' | 'div' - default 'file') -- if 'file', then
#     the graph is saved as a standalone HTML file and `plot`
#     returns None.
#     If 'div', then `plot` returns a string that just contains the
#     HTML <div> that contains the graph and the script to generate the
#     graph.
#     Use 'file' if you want to save and view a single graph at a time
#     in a standalone HTML file.
#     Use 'div' if you are embedding these graphs in an HTML file with
#     other graphs or HTML markup, like a HTML report or an website.
