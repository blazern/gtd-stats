import unittest
from core import test_utils

import os

from core.stats import stats_file_utils
from core.stats.stats_entry import StatsEntry
from core.stats.stats_metadata import StatsMetadata
from core.stats.stats_cluster import StatsCluster

class StatsFileUtilsTests(unittest.TestCase):
  def test_can_load_stats_from_file(self):
    file_contents = 'date;value;id\n06/04/2019;1;hello\n07/04/2019;2;world'
    file_path = test_utils.make_file_and_write(test_utils.make_tmp_dir(), file_contents)
    stats_cluster = stats_file_utils.load_from(file_path)

    self.assertEqual(StatsMetadata.from_str('date;value;id'), stats_cluster.metadata())
    self.assertEqual(2, len(stats_cluster.entries()))
    self.assertEqual(StatsEntry.from_str('07/04/2019;2;world'), stats_cluster.entries()[0])
    self.assertEqual(StatsEntry.from_str('06/04/2019;1;hello'), stats_cluster.entries()[1])

  def test_can_save_stats_to_file(self):
    initial_file_contents = ''
    file_path = test_utils.make_file_and_write(test_utils.make_tmp_dir(), initial_file_contents)

    metadata = StatsMetadata.from_str('date;value;id')
    stats_entries = [StatsEntry.from_str('06/04/2019;1;hello'),
                     StatsEntry.from_str('07/04/2019;2;world')]
    stats_file_utils.write_into(file_path, StatsCluster(metadata, stats_entries))

    with open(file_path, 'r') as opened_file:
      file_contents = opened_file.read()

    expected_file_contents = 'date;value;id\n07/04/2019;2;world\n06/04/2019;1;hello'
    self.assertEqual(expected_file_contents, file_contents)

  def test_can_add_stats_to_file(self):
    initial_file_contents = 'date;value;id\n06/04/2019;1;hello\n08/04/2019;2;world'
    file_path = test_utils.make_file_and_write(test_utils.make_tmp_dir(), initial_file_contents)

    stats_file_utils.write_into(file_path,
                                StatsCluster(StatsMetadata.from_str('date;value;id'),
                                             [StatsEntry.from_str('07/04/2019;1;wonderful')]))
    stats_cluster = stats_file_utils.load_from(file_path)
    self.assertEqual(3, len(stats_cluster.entries()))
    self.assertEqual(StatsEntry.from_str('08/04/2019;2;world'), stats_cluster.entries()[0])
    self.assertEqual(StatsEntry.from_str('07/04/2019;1;wonderful'), stats_cluster.entries()[1])
    self.assertEqual(StatsEntry.from_str('06/04/2019;1;hello'), stats_cluster.entries()[2])

  def test_throws_when_no_metadata(self):
    file_contents = '06/04/2000;1;hello'
    file_path = test_utils.make_file_and_write(test_utils.make_tmp_dir(), file_contents)
    exception_caught = False
    try:
      stats_file_utils.load_from(file_path)
    except:
      exception_caught = True
    self.assertTrue(exception_caught)

  def test_ignores_empty_lines_in_file(self):
    file_contents = 'date;value;id\n06/04/2019;1;hello\n\n\n\n\n\n\n07/04/2019;2;world'
    file_path = test_utils.make_file_and_write(test_utils.make_tmp_dir(), file_contents)
    stats_cluster = stats_file_utils.load_from(file_path)
    self.assertEqual(2, len(stats_cluster.entries()))

  def test_ignores_trimmable_whitespaces_in_file(self):
    file_contents = '     date;value;id  \n   06/04/2019;1;hello    \n    07/04/2019;2;world     '
    file_path = test_utils.make_file_and_write(test_utils.make_tmp_dir(), file_contents)
    stats_cluster = stats_file_utils.load_from(file_path)
    self.assertEqual(2, len(stats_cluster.entries()))

  def test_can_save_backup_to_given_folder(self):
    initial_file_contents = ''
    file_path = test_utils.make_file_and_write(test_utils.make_tmp_dir(), initial_file_contents)
    metadata = StatsMetadata.from_str('date;value;comment')

    stats_entries = [StatsEntry.from_str('06/04/2019;1;hello'),
                     StatsEntry.from_str('07/04/2019;2;world')]
    stats_file_utils.write_into(file_path, StatsCluster(metadata, stats_entries))

    stats_entries = [StatsEntry.from_str('08/04/2019;1;goodbye'),
                     StatsEntry.from_str('09/04/2019;2;world')]
    backup_folder = test_utils.make_tmp_dir()
    
    self.assertEqual(0, len(os.listdir(backup_folder)))
    stats_file_utils.write_into(file_path, StatsCluster(metadata, stats_entries), backup_dir_path=backup_folder)

    backup_files = os.listdir(backup_folder)
    backup_file_path = os.path.join(backup_folder, backup_files[0])
    with open(backup_file_path, 'r') as opened_file:
      backup = opened_file.read()
    self.assertEqual('date;value;comment\n07/04/2019;2;world\n06/04/2019;1;hello', backup)

  def test_each_write_creates_backup(self):
    initial_file_contents = ''
    file_path = test_utils.make_file_and_write(test_utils.make_tmp_dir(), initial_file_contents)
    metadata = StatsMetadata.from_str('date;value;comment')

    backup_folder = test_utils.make_tmp_dir()
    self.assertEqual(0, len(os.listdir(backup_folder)))
    stats_file_utils.write_into(file_path,
                                StatsCluster(metadata, [StatsEntry.from_str('06/04/2019;1;hello')]),
                                backup_dir_path=backup_folder)
    self.assertEqual(1, len(os.listdir(backup_folder)))
    stats_file_utils.write_into(file_path,
                                StatsCluster(metadata, [StatsEntry.from_str('07/04/2019;1;hello')]),
                                backup_dir_path=backup_folder)
    self.assertEqual(2, len(os.listdir(backup_folder)))
    stats_file_utils.write_into(file_path,
                                StatsCluster(metadata, [StatsEntry.from_str('07/04/2019;1;hello')]),
                                backup_dir_path=backup_folder)
    self.assertEqual(3, len(os.listdir(backup_folder)))

  def test_can_remove_too_old_backups(self):
    initial_file_contents = ''
    file_path = test_utils.make_file_and_write(test_utils.make_tmp_dir(), initial_file_contents)
    metadata = StatsMetadata.from_str('date;value;comment')

    backup_folder = test_utils.make_tmp_dir()
    stats_file_utils.write_into(file_path,
                                StatsCluster(metadata, [StatsEntry.from_str('06/04/2019;1;hello')]),
                                backup_dir_path=backup_folder,
                                backups_limit=2)
    stats_file_utils.write_into(file_path,
                                StatsCluster(metadata, [StatsEntry.from_str('07/04/2019;1;wonderful')]),
                                backup_dir_path=backup_folder,
                                backups_limit=2)
    stats_file_utils.write_into(file_path,
                                StatsCluster(metadata, [StatsEntry.from_str('08/04/2019;1;world')]),
                                backup_dir_path=backup_folder,
                                backups_limit=2)
    stats_file_utils.write_into(file_path,
                                StatsCluster(metadata, [StatsEntry.from_str('09/04/2019;1;bye')]),
                                backup_dir_path=backup_folder,
                                backups_limit=2)
    
    backup_files = os.listdir(backup_folder)
    self.assertEqual(2, len(backup_files))

    backups = []
    for backup_file in backup_files:
      backup_file_path = os.path.join(backup_folder, backup_file)
      with open(backup_file_path, 'r') as opened_file:
        backups.append(opened_file.read())
    self.assertTrue('date;value;comment\n07/04/2019;1;wonderful\n06/04/2019;1;hello' in backups)
    self.assertTrue('date;value;comment\n08/04/2019;1;world\n07/04/2019;1;wonderful\n06/04/2019;1;hello' in backups)

  def test_empty_file_cannot_be_transformed_to_stats_cluster(self):
    initial_file_contents = ''
    file_path = test_utils.make_file_and_write(test_utils.make_tmp_dir(), initial_file_contents)
    stats_cluster = stats_file_utils.load_from(file_path)
    self.assertEqual(None, stats_cluster)
