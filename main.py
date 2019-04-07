#!/usr/bin/env python3.7

import argparse
import sys
import re

from datetime import datetime

from commits_stats import extract_commits_history
from commits_stats import convert_commits_to_stats_entries

def extract_date_from(date_str, default_value):
  if date_str is None:
    date_str = default_value
  date_pattern = re.compile("^\d\d\d\d-\d\d-\d\d$")
  if not date_pattern.match(date_str):
    raise ValueError('Invalid date: {}'.format(date_str))
  return date_str

def main(argv):
  parser = argparse.ArgumentParser(description='Produces commits history for given period')
  parser.add_argument('--repo-path', required=True)
  parser.add_argument('--authors', nargs='*', help='List of commits authors to process')
  parser.add_argument('--start-date')
  parser.add_argument('--end-date', help='Used for Git\'s "--after" param.') # TODO: write here
  options = parser.parse_args()

  start_date = extract_date_from(options.start_date, '2000-01-01')
  end_date = extract_date_from(options.end_date, '2099-12-31')
  authors = options.authors
  if authors is None:
    authors = []

  commits = extract_commits_history(options.repo_path, start_date, end_date, authors)
  stats_entries = convert_commits_to_stats_entries(commits)
  stats_entries = reversed(stats_entries)
  for stats_entry in stats_entries:
    print(str(stats_entry))

if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))