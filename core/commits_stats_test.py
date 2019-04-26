import unittest
import core.test_utils as test_utils

import os
import time
from subprocess import DEVNULL
from datetime import datetime
from random import random

from core.commits_stats import extract_commits_history
from core.commits_stats import convert_commits_to_stats_entries
from core.utils import check_call
from core.utils import check_output

def date_to_timestamp(date):
  return time.mktime(date.timetuple())

def date_str_to_timestamp(date_str):
  return date_to_timestamp(datetime.strptime(date_str, '%Y-%m-%d'))

def str_to_file(file_path, string):
  with open(file_path, "w") as text_file:
    text_file.write(string)

def make_commit(repo_path, date, author, msg):
  # First init will initialize the repo, following inits
  # will do nothing
  check_call('git -C {} init'.format(repo_path), DEVNULL)

  test_utils.make_file_and_write(repo_path, str(random()))
  check_call('git -C {} add -A'.format(repo_path),
             DEVNULL)
  check_call('GIT_AUTHOR_DATE="{0} 00:00" GIT_COMMITTER_DATE="{0} 00:00" '
             'git -C {1} commit --author "{2}" -m "{3}"'.format(date, repo_path, author, msg),
             DEVNULL)

class CommitStatsTests(unittest.TestCase):
  def test_can_get_full_commits_history(self):
    repo_path = test_utils.make_tmp_dir()
    make_commit(repo_path, '2001-01-01', 'name1 <email1@host.com>', 'init commit')
    make_commit(repo_path, '2002-01-01', 'name2 <email2@host.com>', 'commit2')
    make_commit(repo_path, '2003-01-01', 'name3 <email3@host.com>', 'last commit')

    commits = extract_commits_history(repo_path, '2000-01-01', '2003-01-02')
    
    self.assertEqual(3, len(commits))
    
    self.assertEqual(date_str_to_timestamp('2001-01-01'), date_to_timestamp(commits[0].date))
    self.assertEqual(date_str_to_timestamp('2002-01-01'), date_to_timestamp(commits[1].date))
    self.assertEqual(date_str_to_timestamp('2003-01-01'), date_to_timestamp(commits[2].date))

    self.assertEqual('init commit', commits[0].msg)
    self.assertEqual('commit2', commits[1].msg)
    self.assertEqual('last commit', commits[2].msg)

    self.assertEqual('name1', commits[0].author)
    self.assertEqual('name2', commits[1].author)
    self.assertEqual('name3', commits[2].author)

    sha1s = check_output('git -C {} log --format=format:"%H"'.format(repo_path),
                         print_cmd=False).split('\n')
    sha1s = list(reversed(sha1s))
    self.assertEqual(sha1s[0], commits[0].sha1)
    self.assertEqual(sha1s[1], commits[1].sha1)
    self.assertEqual(sha1s[2], commits[2].sha1)

  def test_can_get_commit_history_without_recent(self):
    repo_path = test_utils.make_tmp_dir()
    make_commit(repo_path, '2001-01-01', 'name1 <email1@host.com>', 'init commit')
    make_commit(repo_path, '2002-01-01', 'name2 <email2@host.com>', 'commit2')
    make_commit(repo_path, '2003-01-01', 'name3 <email3@host.com>', 'last commit')

    commits = extract_commits_history(repo_path, '2000-01-01', '2002-01-02')
    
    self.assertEqual(2, len(commits))
    
    self.assertEqual(date_str_to_timestamp('2001-01-01'), date_to_timestamp(commits[0].date))
    self.assertEqual(date_str_to_timestamp('2002-01-01'), date_to_timestamp(commits[1].date))

    self.assertEqual('init commit', commits[0].msg)
    self.assertEqual('commit2', commits[1].msg)

    self.assertEqual('name1', commits[0].author)
    self.assertEqual('name2', commits[1].author)

    sha1s = check_output('git -C {} log --format=format:"%H"'.format(repo_path),
                         print_cmd=False).split('\n')
    sha1s = list(reversed(sha1s))
    self.assertEqual(sha1s[0], commits[0].sha1)
    self.assertEqual(sha1s[1], commits[1].sha1)

  def test_can_get_commit_history_without_older(self):
    repo_path = test_utils.make_tmp_dir()
    make_commit(repo_path, '2001-01-01', 'name1 <email1@host.com>', 'init commit')
    make_commit(repo_path, '2002-01-01', 'name2 <email2@host.com>', 'commit2')
    make_commit(repo_path, '2003-01-01', 'name3 <email3@host.com>', 'last commit')

    commits = extract_commits_history(repo_path, '2001-01-02', '2003-01-02')
    
    self.assertEqual(2, len(commits))
    
    self.assertEqual(date_str_to_timestamp('2002-01-01'), date_to_timestamp(commits[0].date))
    self.assertEqual(date_str_to_timestamp('2003-01-01'), date_to_timestamp(commits[1].date))

    self.assertEqual('commit2', commits[0].msg)
    self.assertEqual('last commit', commits[1].msg)

    self.assertEqual('name2', commits[0].author)
    self.assertEqual('name3', commits[1].author)

    sha1s = check_output('git -C {} log --format=format:"%H"'.format(repo_path),
                         print_cmd=False).split('\n')
    sha1s = list(reversed(sha1s))
    self.assertEqual(sha1s[1], commits[0].sha1)
    self.assertEqual(sha1s[2], commits[1].sha1)

  def test_can_choose_authors(self):
    repo_path = test_utils.make_tmp_dir()
    make_commit(repo_path, '2001-01-01', 'name1 <email1@host.com>', 'init commit')
    make_commit(repo_path, '2002-01-01', 'name2 <email2@host.com>', 'commit2')
    make_commit(repo_path, '2003-01-01', 'name3 <email3@host.com>', 'last commit')

    commits = extract_commits_history(repo_path, '2000-01-01', '2003-01-02',
                                      authors = ['name1', 'name3'])

    self.assertEqual(2, len(commits))

    self.assertEqual(date_str_to_timestamp('2001-01-01'), date_to_timestamp(commits[0].date))
    self.assertEqual(date_str_to_timestamp('2003-01-01'), date_to_timestamp(commits[1].date))

    self.assertEqual('init commit', commits[0].msg)
    self.assertEqual('last commit', commits[1].msg)

    self.assertEqual('name1', commits[0].author)
    self.assertEqual('name3', commits[1].author)

    sha1s = check_output('git -C {} log --format=format:"%H"'.format(repo_path),
                         print_cmd=False).split('\n')
    sha1s = list(reversed(sha1s))
    self.assertEqual(sha1s[0], commits[0].sha1)
    self.assertEqual(sha1s[2], commits[1].sha1)

  def test_convert_commits_to_stats_entries(self):
    repo_path = test_utils.make_tmp_dir()
    make_commit(repo_path, '2001-01-01', 'name1 <email1@host.com>', 'init commit')
    make_commit(repo_path, '2002-01-01', 'name2 <email2@host.com>', 'commit2')
    make_commit(repo_path, '2003-01-01', 'name3 <email3@host.com>', 'pre last commit')
    make_commit(repo_path, '2001-01-01', 'name1 <email1@host.com>', 'last commit')

    commits = extract_commits_history(repo_path, '2000-01-01', '2003-01-02')
    self.assertEqual(4, len(commits))

    stats_entries = convert_commits_to_stats_entries(commits)
    self.assertEqual(3, len(stats_entries))
    self.assertEqual('01/01/2001;2;name1', str(stats_entries[0]))
    self.assertEqual('01/01/2002;1;name2', str(stats_entries[1]))
    self.assertEqual('01/01/2003;1;name3', str(stats_entries[2]))

  def test_convert_commits_to_stats_entries_with_aliases(self):
    repo_path = test_utils.make_tmp_dir()
    make_commit(repo_path, '2001-01-01', 'name1 <email1@host.com>', 'init commit')
    make_commit(repo_path, '2002-01-01', 'name2 <email2@host.com>', 'commit2')
    make_commit(repo_path, '2002-01-01', 'name3 <email3@host.com>', 'pre last commit')
    make_commit(repo_path, '2001-01-01', 'name1 <email1@host.com>', 'last commit')

    commits = extract_commits_history(repo_path, '2000-01-01', '2003-01-02')
    self.assertEqual(4, len(commits))

    aliases = {'name2':['name3']}
    stats_entries = convert_commits_to_stats_entries(commits, aliases=aliases)
    self.assertEqual(2, len(stats_entries))
    self.assertEqual('01/01/2001;2;name1', str(stats_entries[0]))
    self.assertEqual('01/01/2002;2;name2', str(stats_entries[1]))

  def test_authors_with_whitespaces_handled_properly(self):
    repo_path = test_utils.make_tmp_dir()
    make_commit(repo_path, '2001-01-01', 'firstname secondname <email1@host.com>', 'init commit')

    commits = extract_commits_history(repo_path, '2000-01-01', '2003-01-02')
    
    self.assertEqual(1, len(commits))
    self.assertEqual(date_str_to_timestamp('2001-01-01'), date_to_timestamp(commits[0].date))
    self.assertEqual('init commit', commits[0].msg)
    self.assertEqual('firstname secondname', commits[0].author)

    sha1s = check_output('git -C {} log --format=format:"%H"'.format(repo_path),
                         print_cmd=False).split('\n')
    sha1s = list(reversed(sha1s))
    self.assertEqual(sha1s[0], commits[0].sha1)

