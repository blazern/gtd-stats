import unittest
import test_utils

import os

import stats_file_utils
from stats_entry import StatsEntry

class StatsFileUtilsTests(unittest.TestCase):
  def test_can_load_stats_from_file(self):
    file_contents = '06/04/2019;1;hello\n07/04/2019;2;world'
    file_path = test_utils.make_file_and_write(test_utils.make_tmp_dir(), file_contents)
    stats_entries = stats_file_utils.load_from(file_path)

    self.assertEqual(2, len(stats_entries))
    self.assertEqual(StatsEntry.from_str('06/04/2019;1;hello'), stats_entries[0])
    self.assertEqual(StatsEntry.from_str('07/04/2019;2;world'), stats_entries[1])

  def test_can_save_stats_to_file(self):
    initial_file_contents = ''
    file_path = test_utils.make_file_and_write(test_utils.make_tmp_dir(), initial_file_contents)

    stats_entries = [StatsEntry.from_str('06/04/2019;1;hello'),
                     StatsEntry.from_str('07/04/2019;2;world')]
    stats_file_utils.write_into(file_path, stats_entries)

    with open(file_path, 'r') as opened_file:
      file_contents = opened_file.read()

    expected_file_contents = '06/04/2019;1;hello\n07/04/2019;2;world'
    self.assertEqual(expected_file_contents, file_contents)

  def test_can_add_stats_to_file(self):
    initial_file_contents = '06/04/2019;1;hello\n08/04/2019;2;world'
    file_path = test_utils.make_file_and_write(test_utils.make_tmp_dir(), initial_file_contents)

    stats_file_utils.write_into(file_path, [StatsEntry.from_str('07/04/2019;1;wonderful')])
    stats_entries = stats_file_utils.load_from(file_path)
    self.assertEqual(3, len(stats_entries))
    self.assertEqual(StatsEntry.from_str('06/04/2019;1;hello'), stats_entries[0])
    self.assertEqual(StatsEntry.from_str('07/04/2019;1;wonderful'), stats_entries[1])
    self.assertEqual(StatsEntry.from_str('08/04/2019;2;world'), stats_entries[2])

  def test_throws_when_invalid_input(self):
    file_contents = '06/04/0;1;hello'
    file_path = test_utils.make_file_and_write(test_utils.make_tmp_dir(), file_contents)
    exception_caught = False
    try:
      stats_file_utils.load_from(file_path)
    except:
      exception_caught = True
    self.assertTrue(exception_caught)

  def test_ignores_empty_lines_in_file(self):
    file_contents = '06/04/2019;1;hello\n\n\n\n\n\n\n07/04/2019;2;world'
    file_path = test_utils.make_file_and_write(test_utils.make_tmp_dir(), file_contents)
    stats_entries = stats_file_utils.load_from(file_path)
    self.assertEqual(2, len(stats_entries))

  def test_ignores_trimmable_whitespaces_in_file(self):
    file_contents = '     06/04/2019;1;hello    \n    07/04/2019;2;world     '
    file_path = test_utils.make_file_and_write(test_utils.make_tmp_dir(), file_contents)
    stats_entries = stats_file_utils.load_from(file_path)
    self.assertEqual(2, len(stats_entries))

  def test_can_save_backup_to_given_folder(self):
    initial_file_contents = ''
    file_path = test_utils.make_file_and_write(test_utils.make_tmp_dir(), initial_file_contents)

    stats_entries = [StatsEntry.from_str('06/04/2019;1;hello'),
                     StatsEntry.from_str('07/04/2019;2;world')]
    stats_file_utils.write_into(file_path, stats_entries)

    stats_entries = [StatsEntry.from_str('08/04/2019;1;goodbye'),
                     StatsEntry.from_str('09/04/2019;2;world')]
    backup_folder = test_utils.make_tmp_dir()
    
    self.assertEqual(0, len(os.listdir(backup_folder)))
    stats_file_utils.write_into(file_path, stats_entries, backup_dir_path=backup_folder)

    backup_files = os.listdir(backup_folder)
    backup_file_path = os.path.join(backup_folder, backup_files[0])
    with open(backup_file_path, 'r') as opened_file:
      backup = opened_file.read()
    self.assertEqual('06/04/2019;1;hello\n07/04/2019;2;world', backup)

  def test_each_write_creates_backup(self):
    initial_file_contents = ''
    file_path = test_utils.make_file_and_write(test_utils.make_tmp_dir(), initial_file_contents)

    backup_folder = test_utils.make_tmp_dir()
    self.assertEqual(0, len(os.listdir(backup_folder)))
    stats_file_utils.write_into(file_path,
                                [StatsEntry.from_str('06/04/2019;1;hello')],
                                backup_dir_path=backup_folder)
    self.assertEqual(1, len(os.listdir(backup_folder)))
    stats_file_utils.write_into(file_path,
                                [StatsEntry.from_str('07/04/2019;1;hello')],
                                backup_dir_path=backup_folder)
    self.assertEqual(2, len(os.listdir(backup_folder)))
    stats_file_utils.write_into(file_path,
                                [StatsEntry.from_str('07/04/2019;1;hello')],
                                backup_dir_path=backup_folder)
    self.assertEqual(3, len(os.listdir(backup_folder)))

  def test_can_remove_too_old_backups(self):
    initial_file_contents = ''
    file_path = test_utils.make_file_and_write(test_utils.make_tmp_dir(), initial_file_contents)

    backup_folder = test_utils.make_tmp_dir()
    stats_file_utils.write_into(file_path,
                                [StatsEntry.from_str('06/04/2019;1;hello')],
                                backup_dir_path=backup_folder,
                                backups_limit=2)
    stats_file_utils.write_into(file_path,
                                [StatsEntry.from_str('07/04/2019;1;wonderful')],
                                backup_dir_path=backup_folder,
                                backups_limit=2)
    stats_file_utils.write_into(file_path,
                                [StatsEntry.from_str('08/04/2019;1;world')],
                                backup_dir_path=backup_folder,
                                backups_limit=2)
    stats_file_utils.write_into(file_path,
                                [StatsEntry.from_str('09/04/2019;1;bye')],
                                backup_dir_path=backup_folder,
                                backups_limit=2)
    
    backup_files = os.listdir(backup_folder)
    self.assertEqual(2, len(backup_files))

    backups = []
    for backup_file in backup_files:
      backup_file_path = os.path.join(backup_folder, backup_file)
      with open(backup_file_path, 'r') as opened_file:
        backups.append(opened_file.read())
    self.assertTrue('06/04/2019;1;hello\n07/04/2019;1;wonderful' in backups)
    self.assertTrue('06/04/2019;1;hello\n07/04/2019;1;wonderful\n08/04/2019;1;world' in backups)
