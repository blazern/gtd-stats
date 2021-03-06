#!/usr/bin/env python3.7

import argparse
import sys
import re

from datetime import datetime

import core.stats.stats_file_utils
from core.stats.stats_entry import StatsEntry
from core.git.commits_stats import extract_commits_history
from core.git.commits_stats import convert_commits_to_stats_cluster
from core.git.commits_stats import validate_commits_authors_aliases

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

def extract_full_authors_list(input_authors, aliases):
  if input_authors is None:
    return []
  authors = list(input_authors)
  for author, author_aliases in aliases.items():
    if input_authors is not None and author not in input_authors:
      raise ValueError('Author {} is present in --author-aliases but not in --authors'.format(author))
    # If alias is not in the authors list, add it to the list
    # so that commits of the alias would be extracted from the log, too.
    for alias in author_aliases:
      if alias not in authors:
        authors.append(alias)
  return authors

def main(argv):
  parser = argparse.ArgumentParser(description='Produces commits history for given period')
  parser.add_argument('--repos', required=True, help='Paths to git repos, separated by ":".')
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
  aliases = extract_author_aliases_from(options.author_aliases)
  authors = extract_full_authors_list(options.authors, aliases)

  commits = []
  repos = options.repos.split(':')
  for repo in repos:
    commits += extract_commits_history(repo, start_date, end_date, authors)
  stats_cluster = convert_commits_to_stats_cluster(commits, aliases)

  if options.extra_input_file is not None:
    file_stats_cluster = core.stats.stats_file_utils.load_from(options.extra_input_file)
    stats_cluster = stats_cluster.merge(file_stats_cluster, prioritized=stats_cluster)

  if options.output_file is not None:
    core.stats.stats_file_utils.write_into(options.output_file,
                                stats_cluster,
                                options.backups_dir,
                                options.backups_limit)
  else:
    print(str(stats_cluster))

if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
