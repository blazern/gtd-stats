#!/usr/bin/env python3

import os
import time
import unittest
from subprocess import DEVNULL
from datetime import datetime
from random import random

from commits_stats import extract_commits_history
from utils import check_call
from utils import check_output

def date_str_to_timestamp(date_str):
  return time.mktime(datetime.strptime(date_str, "%Y-%m-%d").timetuple())

def str_to_file(file_path, string):
  with open(file_path, "w") as text_file:
    text_file.write(string)

def make_commit(repo_path, date, author, msg):
  # First init will initialize the repo, following inits
  # will do nothing
  check_call('git -C {} init'.format(repo_path), DEVNULL)

  new_file_name = str(random())
  new_file_content = str(random())
  str_to_file(os.path.join(repo_path, new_file_name), new_file_content)
  check_call('git -C {} add -A'.format(repo_path),
             DEVNULL)
  check_call('GIT_AUTHOR_DATE="{0} 00:00" GIT_COMMITTER_DATE="{0} 00:00" '
             'git -C {1} commit --author "{2}" -m "{3}"'.format(date, repo_path, author, msg),
             DEVNULL)

class Tests(unittest.TestCase):
  def test_can_get_full_commits_history(self):
    repo_name = str(datetime.now().microsecond) + str(random())
    repo_path = os.path.join('/tmp/', repo_name)
    os.makedirs(repo_path)
    make_commit(repo_path, '2001-01-01', 'name1 <email1@host.com>', 'init commit')
    make_commit(repo_path, '2002-01-01', 'name2 <email2@host.com>', 'commit2')
    make_commit(repo_path, '2003-01-01', 'name3 <email3@host.com>', 'last commit')

    commits = extract_commits_history(repo_path, '2000-01-01', '2003-01-02')
    
    self.assertEqual(3, len(commits))
    
    self.assertEqual(date_str_to_timestamp('2001-01-01'), commits[0].timestamp)
    self.assertEqual(date_str_to_timestamp('2002-01-01'), commits[1].timestamp)
    self.assertEqual(date_str_to_timestamp('2003-01-01'), commits[2].timestamp)

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
    repo_name = str(datetime.now().microsecond) + str(random())
    repo_path = os.path.join('/tmp/', repo_name)
    os.makedirs(repo_path)
    make_commit(repo_path, '2001-01-01', 'name1 <email1@host.com>', 'init commit')
    make_commit(repo_path, '2002-01-01', 'name2 <email2@host.com>', 'commit2')
    make_commit(repo_path, '2003-01-01', 'name3 <email3@host.com>', 'last commit')

    commits = extract_commits_history(repo_path, '2000-01-01', '2002-01-02')
    
    self.assertEqual(2, len(commits))
    
    self.assertEqual(date_str_to_timestamp('2001-01-01'), commits[0].timestamp)
    self.assertEqual(date_str_to_timestamp('2002-01-01'), commits[1].timestamp)

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
    repo_name = str(datetime.now().microsecond) + str(random())
    repo_path = os.path.join('/tmp/', repo_name)
    os.makedirs(repo_path)
    make_commit(repo_path, '2001-01-01', 'name1 <email1@host.com>', 'init commit')
    make_commit(repo_path, '2002-01-01', 'name2 <email2@host.com>', 'commit2')
    make_commit(repo_path, '2003-01-01', 'name3 <email3@host.com>', 'last commit')

    commits = extract_commits_history(repo_path, '2001-01-02', '2003-01-02')
    
    self.assertEqual(2, len(commits))
    
    self.assertEqual(date_str_to_timestamp('2002-01-01'), commits[0].timestamp)
    self.assertEqual(date_str_to_timestamp('2003-01-01'), commits[1].timestamp)

    self.assertEqual('commit2', commits[0].msg)
    self.assertEqual('last commit', commits[1].msg)

    self.assertEqual('name2', commits[0].author)
    self.assertEqual('name3', commits[1].author)

    sha1s = check_output('git -C {} log --format=format:"%H"'.format(repo_path),
                         print_cmd=False).split('\n')
    sha1s = list(reversed(sha1s))
    self.assertEqual(sha1s[1], commits[0].sha1)
    self.assertEqual(sha1s[2], commits[1].sha1)