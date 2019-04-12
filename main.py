#!/usr/bin/env python3.7

import argparse
import sys
import re

from datetime import datetime

from commits_stats import extract_commits_history
from commits_stats import convert_commits_to_stats_entries
from commits_stats import validate_commits_authors_aliases

def extract_date_from(date_str):
  date_pattern = re.compile('^\d\d\d\d-\d\d-\d\d$')
  if not date_pattern.match(date_str):
    raise ValueError('Invalid date: {}'.format(date_str))
  return date_str

def extract_author_aliases_from(aliases_str):
  if aliases_str is None:
    return {}
  aliases_pattern_str = '^(\w+ ?)+:(\w+ ?)+(;(\w+ ?)+:(\w+ ?)+)*$'
  aliases_pattern = re.compile(aliases_pattern_str)
  if not aliases_pattern.match(aliases_str):
    raise ValueError('Pattern {} is not match by aliases {}'.format(aliases_pattern_str, aliases_str))
  
  aliases_pairs = aliases_str.split(';')
  authors_and_aliases = {}
  for pair in aliases_pairs:
    pair_split = pair.split(':')
    author = pair_split[0]
    alias = pair_split[1]
    if author not in authors_and_aliases:
      authors_and_aliases[author] = []
    authors_and_aliases[author].append(alias)

  validate_commits_authors_aliases(authors_and_aliases)
  return authors_and_aliases

def main(argv):
  parser = argparse.ArgumentParser(description='Produces commits history for given period')
  parser.add_argument('--repo-path', required=True)
  parser.add_argument('--authors', nargs='*', help='List of commits authors to process')
  parser.add_argument('--start-date', default='2000-01-01', help='Used for Git\'s "--until" param. Default is 2000-01-01.')
  parser.add_argument('--end-date', default='2099-12-31', help='Used for Git\'s "--after" param. Default is 2099-12-31.')
  parser.add_argument('--author-aliases', help='List of authors aliases in format ' +
                                               '"author:alias1;author:alias2;author2:alias3;...". ' + 
                                               'This is useful when 1 user made commits as ' +
                                               'several different Git authors.')
  options = parser.parse_args()

  start_date = extract_date_from(options.start_date)
  end_date = extract_date_from(options.end_date)
  authors = options.authors
  if authors is None:
    authors = []

  commits = extract_commits_history(options.repo_path, start_date, end_date, authors)
  aliases = extract_author_aliases_from(options.author_aliases)
  stats_entries = convert_commits_to_stats_entries(commits, aliases)
  stats_entries = reversed(stats_entries)
  for stats_entry in stats_entries:
    print(str(stats_entry))

if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))