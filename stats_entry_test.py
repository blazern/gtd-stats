import unittest

from datetime import datetime

from stats_entry import StatsEntry

class CommitTests(unittest.TestCase):
  def test_str_format(self):
    stats_entry = StatsEntry(datetime.strptime('2019-04-06', '%Y-%m-%d'),
                             123,
                             'hello, world')
    self.assertEqual('06/04/2019;123;hello, world', str(stats_entry))

  def test_creating_from_str(self):
    stats_entry = StatsEntry.from_str('06/04/2019;123;hello, world')
    self.assertEqual(datetime.strptime('2019-04-06', '%Y-%m-%d'), stats_entry.date)
    self.assertEqual(123, stats_entry.value)
    self.assertEqual('hello, world', stats_entry.description)

  def test_creating_from_invalid_str(self):
    caught = False
    try:
      stats_entry = StatsEntry.from_str('06/4/2019;123;hello, world')
    except:
      caught = True
    self.assertTrue(caught)

  def test_can_collapse_stats_entries(self):
    stats_entries = [StatsEntry.from_str('06/04/2019;1;hello'),
                     StatsEntry.from_str('07/04/2019;1;world'),
                     StatsEntry.from_str('06/04/2019;1;hello'),
                     StatsEntry.from_str('08/04/2019;1;world'),
                     StatsEntry.from_str('07/04/2019;1;world')]
    stats_entries = StatsEntry.collapse(stats_entries)
    self.assertEqual(3, len(stats_entries))
    self.assertTrue(StatsEntry.from_str('06/04/2019;2;hello') in stats_entries)
    self.assertTrue(StatsEntry.from_str('07/04/2019;2;world') in stats_entries)
    self.assertTrue(StatsEntry.from_str('08/04/2019;1;world') in stats_entries)

  def test_collapsing_sorts_entries_by_date(self):
    stats_entries = [StatsEntry.from_str('06/04/2019;1;hello'),
                     StatsEntry.from_str('05/04/2019;1;world'),
                     StatsEntry.from_str('04/04/2019;1;!')]
    stats_entries = StatsEntry.collapse(stats_entries)
    self.assertEqual(StatsEntry.from_str('04/04/2019;1;!'), stats_entries[0])
    self.assertEqual(StatsEntry.from_str('05/04/2019;1;world'), stats_entries[1])
    self.assertEqual(StatsEntry.from_str('06/04/2019;1;hello'), stats_entries[2])