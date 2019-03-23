import argparse
import sys
import subprocess
import re

from commit import Commit
from utils import check_call
from utils import check_output

def extract_commits_history(repo_path, start_date, end_date):
  output = check_output('git -C {} log --after={} --until={} --format=format:"%H %at %aN %s"'.format(repo_path, start_date, end_date),
                        print_cmd=False)
  commits_texts = output.split('\n')
  commits = []
  for commit_text in commits_texts:
    time_index = commit_text.index(' ') + 1
    author_index = commit_text.index(' ', time_index) + 1
    msg_index = commit_text.index(' ', author_index) + 1
    
    sha1_hash = commit_text[:time_index - 1]
    time = int(commit_text[time_index:author_index - 1])
    author = commit_text[author_index:msg_index - 1]
    msg = commit_text[msg_index:]
    
    commits.append(Commit(sha1_hash, time, author, msg))
  return list(reversed(commits))