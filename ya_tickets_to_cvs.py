#!/usr/bin/env python3.7

import argparse
import sys
import re
import json
import urllib.request

from datetime import datetime

import core.stats.stats_file_utils
from core.stats.stats_entry import *
from core.stats.stats_cluster import *
from core.stats.stats_metadata import *
from core.stats.stat_column_type import *
from core.stats.typed_stats_entry import *

class Ticket:
  def __init__(self, json_obj):
    self.json_obj = json_obj

  def get_get_resolution_date(self):
    if 'resolvedAt' not in self.json_obj:
      return None
    return datetime.strptime(self.json_obj['resolvedAt'], '%Y-%m-%dT%H:%M:%S.%f%z')

  def get_sp(self):
    if 'storyPoints' not in self.json_obj:
      return 1
    return self.json_obj['storyPoints']

  def get_assignee(self):
    return self.json_obj['assignee']['id']

def tickets_to_stats_cluster(tickets):
  metadata = StatsMetadata.from_str('date;value:sp;value:count;id')
  entries = []
  for ticket in tickets:
    resolution_date = ticket.get_get_resolution_date()
    if resolution_date is None:
      continue
    # The 1 value will be collapsed with tickets in the same day anyway
    columns_values = [resolution_date, ticket.get_sp(), 1, ticket.get_assignee()]
    entry = TypedStatsEntry.from_stats(metadata.types(), columns_values)
    entries.append(entry)

  entries = sorted(entries, key=lambda entry: entry.date())
  return StatsCluster.from_typed_entries(entries, metadata).collapse()

def main(argv):
  parser = argparse.ArgumentParser(description='Produces tickets count and SP resolves stats')
  parser.add_argument('--oauth', required=True, help='See https://wiki.yandex-team.ru/tracker/api/#avtorizacija')
  parser.add_argument('--output-file', required=False, help='File to write stats to instead of stdout')
  parser.add_argument('--backups-dir', help='Path to dir where the script will put backups of the output-file if ' +
                                            'output-file already exists.')
  parser.add_argument('--backups-limit', type=int, help='Max number of backup files. By default, there\'s not limit')
  parser.add_argument('--assignees', required=True, nargs='*', help='List assignees')
  options = parser.parse_args()

  url = "https://st-api.yandex-team.ru/v2/issues?filter=queue:ABRO&filter=assignee:{}&perPage=100&page={}"
  hdr = { 'Authorization' : 'OAuth {}'.format(options.oauth) }
  
  tickets = []
  for assignee in options.assignees:
    should_request_more = True
    next_page_index = 1
    while should_request_more:
      req = urllib.request.Request(url.format(assignee, next_page_index), headers=hdr)
      try:
        response = urllib.request.urlopen(req).read()
      except urllib.error.HTTPError as e:
        sys.stderr.write('Error response code {}, msg: {}, url: {} \n'.format(e.code, e.msg, req.full_url))
        sys.exit(1)
        return

      response = json.loads(response)
      for ticket_json in response:
        tickets.append(Ticket(ticket_json))
      should_request_more = len(response) > 0
      next_page_index += 1

  stats_cluster = tickets_to_stats_cluster(tickets)

  if options.output_file is not None:
    core.stats.stats_file_utils.write_into(options.output_file,
                                stats_cluster,
                                options.backups_dir,
                                options.backups_limit)
  else:
    print(str(stats_cluster))

if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
