import os
import shutil
from datetime import datetime

from core.stats_entry import StatsEntry
from core.stats_cluster import StatsCluster

def load_from(file_path):
  if not os.path.exists(file_path):
    return []

  with open(file_path, 'r') as text_file:
    lines = text_file.readlines()
  lines = [line.strip() for line in lines]
  lines = [line for line in lines if len(line) > 0]
  text = '\n'.join(lines)

  if len(text) is 0:
    return None
  return StatsCluster.from_str(text)

def __handle_backups_before_writing(file_path, backup_dir_path, backups_limit):
  if not os.path.exists(file_path) or backup_dir_path is None:
    return
  if not os.path.exists(backup_dir_path):
    os.makedirs(backup_dir_path)
  
  if backups_limit is not None:
    backup_files = os.listdir(backup_dir_path) 
    backup_files_and_microseconds = []
    for backup_file in backup_files:
      backup_word_index = backup_file.rfind('.backup')
      if backup_word_index == -1:
        continue
      backup_file_name_cut = backup_file[:backup_word_index]
      time_delimiter_index = backup_file_name_cut.rfind('_')
      if time_delimiter_index == -1:
        continue
      creation_time_microseconds = float(backup_file_name_cut[time_delimiter_index+1:])
      backup_files_and_microseconds.append((backup_file, creation_time_microseconds))
    backup_files_and_microseconds = sorted(backup_files_and_microseconds,
                                           key=lambda bfam_pair: bfam_pair[1])
    while len(backup_files_and_microseconds) > backups_limit - 1:
      backup_file_path = os.path.join(backup_dir_path, backup_files_and_microseconds[0][0])
      backup_files_and_microseconds.pop(0)
      os.remove(backup_file_path)

  file_name = os.path.basename(file_path)
  backup_file_name = '{}_{}.backup'.format(file_name, str(datetime.now().timestamp()))
  shutil.copyfile(file_path, os.path.join(backup_dir_path, backup_file_name))

# Writes given entries into the given file.
# Doesn't remove already existing entries from the given file,
# instead, uses StatsEntry.merge() to merge old entries and new.
def write_into(file_path, stats_cluster, backup_dir_path=None, backups_limit=None):
  __handle_backups_before_writing(file_path, backup_dir_path, backups_limit)
  existing_cluster = load_from(file_path)
  if existing_cluster is not None:
    stats_cluster = stats_cluster.merge(existing_cluster, prioritized=stats_cluster)
  if not os.path.exists(os.path.dirname(file_path)):
    os.makedirs(os.path.dirname(file_path))
  with open(file_path, 'w') as text_file:
    text_file.write(str(stats_cluster))
