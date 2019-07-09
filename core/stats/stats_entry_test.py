import unittest

from datetime import datetime

from core.stats.stats_entry import StatsEntry

class StatsEntryTests(unittest.TestCase):
  def test_str_format(self):
    stats_entry = StatsEntry(['06/04/2019', '123', 'hello, world'])
    self.assertEqual('06/04/2019;123;hello, world', str(stats_entry))

  def test_creating_from_str(self):
    stats_entry = StatsEntry.from_str('06/04/2019;123;hello, world')
    self.assertEqual(3, len(stats_entry.columns))
    self.assertEqual('06/04/2019', stats_entry.columns[0])
    self.assertEqual('123', stats_entry.columns[1])
    self.assertEqual('hello, world', stats_entry.columns[2])