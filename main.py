#!/usr/bin/env python3.7

import argparse
import sys
import re

from datetime import datetime

import stats_file_utils
from stats_entry import StatsEntry
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
  parser.add_argument('--repo', required=True, help='Path to a git repo.')
  parser.add_argument('--authors', nargs='*', help='List of commits authors to process')
  parser.add_argument('--start-date', default='2000-01-01', help='Used for Git\'s "--until" param. Default is 2000-01-01.')
  parser.add_argument('--end-date', default='2099-12-31', help='Used for Git\'s "--after" param. Default is 2099-12-31.')
  parser.add_argument('--author-aliases', help='List of authors aliases in format ' +
                                               '"author:alias1;author:alias2;author2:alias3;...". ' + 
                                               'This is useful when 1 user made commits as ' +
                                               'several different Git authors.')
  parser.add_argument('--extra-input-file', help='Path to a file with already produced stats which ' +
                                                 'will be used as data about periods beyond our start and end dates. ' +
                                                 'Note that if some stats from the given file overlap with ' +
                                                 'newly produced stats, new stats will be prioritized over file\'s stats ' +
                                                 'because it\'s assumed that currently we have more data than there ' +
                                                 'was at the time of the file creation.')
  parser.add_argument('--output-file', help='Path to output file. If specified, the output will be written ' +
                                            'into the file. If not specified, the output will be printed. ' +
                                            'Note that if the file already exists, it will be overwritten. See --backups-dir.')
  parser.add_argument('--backups-dir', help='Path to dir where the script will put backups of the output-file if ' +
                                            'output-file already exists.')
  parser.add_argument('--backups-limit', type=int, help='Max number of backup files. By default, there\'s not limit')
  options = parser.parse_args()

  start_date = extract_date_from(options.start_date)
  end_date = extract_date_from(options.end_date)
  authors = options.authors
  if authors is None:
    authors = []

  commits = extract_commits_history(options.repo, start_date, end_date, authors)
  aliases = extract_author_aliases_from(options.author_aliases)
  stats_entries = convert_commits_to_stats_entries(commits, aliases)
  stats_entries = list(reversed(stats_entries))
  if options.extra_input_file is not None:
    file_stats = stats_file_utils.load_from(options.extra_input_file)
    stats_entries = StatsEntry.merge(stats_entries, file_stats, prioritized=stats_entries)

  if options.output_file is not None:
    stats_file_utils.write_into(options.output_file,
                                stats_entries,
                                options.backups_dir,
                                options.backups_limit)
  else:
    for stats_entry in stats_entries:
      print(str(stats_entry))

if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))