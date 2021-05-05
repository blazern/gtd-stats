#!/usr/bin/env python3.7

import argparse
import sys
import re
import json

from datetime import datetime
from datetime import timedelta

from core.stats.stats_entry import StatsEntry
from core.stats.stats_cluster import StatsCluster
from core.stats.stats_metadata import StatsMetadata
from core.stats.typed_stats_entry import TypedStatsEntry
from core.stats.stat_column_type import StatColumnType
import core.stats.stats_file_utils


def main(argv):
  parser = argparse.ArgumentParser(description='Produces messages history for given JSON file exported from Telegram')
  parser.add_argument('--json-path', required=True, help='Path JSON file exported from Telegram')
  parser.add_argument('--authors-top', type=int, required=True, help='Number of top authors (by number of their messages) ' +
                                                                     'which will be included into stats')
  parser.add_argument('--mandatory-authors', nargs='*', help='List of authors which must be included into statistics')
  parser.add_argument('--output-file', help='Path to output file. If specified, the output will be written ' +
                                            'into the file. If not specified, the output will be printed. ' +
                                            'Note that if the file already exists, it will be overwritten. See --backups-dir.')
  options = parser.parse_args()

  with open(options.json_path, 'r') as file:
    input_json = json.loads(file.read())

  earliest_date = None
  latest_date = None
  messages = []
  for message_json in input_json['messages']:
    time = datetime.fromisoformat(message_json['date'])
    date = datetime(time.year, time.month, time.day)
    if earliest_date is None or date < earliest_date:
      earliest_date = date
    if latest_date is None or latest_date < date:
      latest_date = date

    if 'from' not in message_json:
      continue
    messages.append({
      'author': message_json['from'],
      'date': date
    })

  messages_by_dates_and_authors = {}
  authors = set()
  messages_by_author = {}
  for message in messages:
    author = message['author']
    date = message['date']
    authors.add(author)
    if author not in messages_by_author:
      messages_by_author[author] = 0
    if date not in messages_by_dates_and_authors:
      messages_by_dates_and_authors[date] = {}
    if author not in messages_by_dates_and_authors[date]:
      messages_by_dates_and_authors[date][author] = 0
    messages_by_dates_and_authors[date][author] += 1
    messages_by_author[author] += 1

  authors_top = []
  for author, messages in messages_by_author.items():
    authors_top.append((author, messages))
  authors_top = sorted(authors_top, reverse=True, key = lambda item: item[1])
  accepted_authors = set(list(authors_top)[:options.authors_top])
  accepted_authors = list(map(lambda item: item[0], accepted_authors))
  if options.mandatory_authors:
    accepted_authors += options.mandatory_authors

  # Fill empty dates
  date = earliest_date
  while date <= latest_date:
    if date not in messages_by_dates_and_authors:
      messages_by_dates_and_authors[date] = {}
    date = date + timedelta(days=1)

  # Fill empty messages
  for date, authors_msgs in messages_by_dates_and_authors.items():
    for author in authors:
      if author not in authors_msgs:
        authors_msgs[author] = 0

  entries = []
  date = earliest_date
  while date <= latest_date:
    authors_msgs = messages_by_dates_and_authors[date]
    for author, msgs in authors_msgs.items():
      if author not in accepted_authors:
        continue
      entry = TypedStatsEntry.from_stats([StatColumnType.DATE, StatColumnType.VALUE, StatColumnType.ID],
                                         [date,                msgs,                 author])
      entries.append(entry)
    date = date + timedelta(days=1)

  metadata = StatsMetadata.from_str("""
===
- what: chart
  title: 7 days moving average
  type: moving-average
  offset: 7
- what: chart
  title: 14 days moving average
  types:
  - type: moving-average
    offset: 14
- what: chart
  title: 30 days moving average
  types:
  - type: moving-average
    offset: 30
- what: chart
  title: month period
  types:
  - type: period
    unit: months
    unit-value: 1
- what: format
  value: date;value;id
===
""")
  cluster = StatsCluster.from_typed_entries(entries, metadata)

  if options.output_file is not None:
    core.stats.stats_file_utils.write_into(options.output_file,
                                cluster)
  else:
    print(str(cluster))

if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
