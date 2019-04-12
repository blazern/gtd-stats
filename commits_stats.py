import argparse
import sys
import subprocess
import re

from datetime import datetime
from utils import check_call
from utils import check_output

from commit import Commit
from stats_entry import StatsEntry

def extract_commits_history(repo_path, start_date, end_date, authors = []):
  output = check_output('git -C {} log --no-merges --after={} --until={} --format=format:"%H;%aI;%aN;%s"'.format(repo_path, start_date, end_date),
                        print_cmd=False)
  commits_texts = output.split('\n')
  commits = []
  for commit_text in commits_texts:
    time_index = commit_text.index(';') + 1
    author_index = commit_text.index(';', time_index) + 1
    msg_index = commit_text.index(';', author_index) + 1

    sha1_hash = commit_text[:time_index - 1]
    commit_datetime = datetime.fromisoformat(commit_text[time_index:author_index - 1])
    author = commit_text[author_index:msg_index - 1]
    msg = commit_text[msg_index:]

    if len(authors) > 0 and author not in authors:
      continue
    commits.append(Commit(sha1_hash, commit_datetime, author, msg))

  return list(reversed(commits))

def validate_commits_authors_aliases(authors_and_aliases):
  all_authors = []
  all_aliases = []
  for author, aliases in authors_and_aliases.items():
    if not isinstance(author, str):
      raise ValueError('Author is not str: {}'.format(author))
    if not isinstance(aliases, list):
      raise ValueError('Aliases is not list: {}'.format(aliases))
    all_authors += [author]
    all_aliases += aliases

  if len(list(set(all_authors) & set(all_aliases))) != 0:
    raise ValueError('Authors and aliases must not intersect, but they do.'
                     + ' Authors: {}, aliases: {}. The arg: {}'.format(all_authors, all_aliases, authors_and_aliases))
  if len(all_aliases) != len(set(all_aliases)):
    raise ValueError('Aliases must be unique, but they\'re not: {}. The arg: {}'.format(all_aliases, authors_and_aliases))

def __reverse_authors_and_aliases(authors_and_aliases):
  validate_commits_authors_aliases(authors_and_aliases)
  aliases_and_authors = {}
  for author, aliases in authors_and_aliases.items():
    for alias in aliases:
      # aliases are guaranteed to be unique
      aliases_and_authors[alias] = author
  return aliases_and_authors

# Aliases dict should have next format: {'author1':['alias1','alias2'], 'author2':['alias3']}
def convert_commits_to_stats_entries(commits, aliases={}):
  aliases_and_authors = __reverse_authors_and_aliases(aliases)
  entries = []
  for commit in commits:
    if commit.author in aliases_and_authors:
      commit = Commit(commit.sha1,
                      commit.date,
                      aliases_and_authors[commit.author],
                      commit.msg)
    entries.append(commit.to_stats_entry())
  return StatsEntry.collapse(entries)