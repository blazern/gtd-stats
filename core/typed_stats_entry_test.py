import unittest

from datetime import datetime

from core.stats_entry import StatsEntry
from core.stats_metadata import StatsMetadata
from core.stat_column_type import StatColumnType
from core.typed_stats_entry import TypedStatsEntry

class TypedStatsEntryTests(unittest.TestCase):
  def test_creating_from_str(self):
    types = [StatColumnType.DATE, StatColumnType.VALUE, StatColumnType.ID, StatColumnType.COMMENT]
    stats_entry = StatsEntry.from_str('06/04/2019;123;hello, world;comment')
    stats_entry = TypedStatsEntry(stats_entry, types)

    self.assertEqual(datetime.strptime('2019-04-06', '%Y-%m-%d'), stats_entry.at(0))
    self.assertEqual(datetime.strptime('2019-04-06', '%Y-%m-%d'), stats_entry.date())

    self.assertEqual(123, stats_entry.at(1))
    self.assertEqual(123, stats_entry.value())

    self.assertEqual('hello, world', stats_entry.at(2))
    self.assertEqual('hello, world', stats_entry.id())

    self.assertEqual('comment', stats_entry.at(3))
    self.assertEqual('comment', stats_entry.comment())

  def test_creating_from_invalid_str(self):
    types = [StatColumnType.DATE, StatColumnType.VALUE, StatColumnType.ID, StatColumnType.COMMENT]
    
    caught = False
    try:
      stats_entry = StatsEntry.from_str('06/04/2019;123;hello, world;comment')
      stats_entry = TypedStatsEntry(stats_entry, types)
      typed.date()
    except:
      caught = True
    self.assertTrue(caught)

  def test_no_stat_column_type_means_none_value(self):
    typed_stats_entry = TypedStatsEntry(StatsEntry.from_str('123;hello, world;comment'),
                                        [StatColumnType.VALUE, StatColumnType.ID, StatColumnType.COMMENT])
    self.assertEqual(None, typed_stats_entry.date())
    self.assertNotEqual(None, typed_stats_entry.value())
    self.assertNotEqual(None, typed_stats_entry.id())
    self.assertNotEqual(None, typed_stats_entry.comment())

    typed_stats_entry = TypedStatsEntry(StatsEntry.from_str('06/04/2019;hello, world;comment'),
                                        [StatColumnType.DATE, StatColumnType.ID, StatColumnType.COMMENT])
    self.assertNotEqual(None, typed_stats_entry.date())
    self.assertEqual(None, typed_stats_entry.value())
    self.assertNotEqual(None, typed_stats_entry.id())
    self.assertNotEqual(None, typed_stats_entry.comment())

    typed_stats_entry = TypedStatsEntry(StatsEntry.from_str('06/04/2019;123;comment'),
                                        [StatColumnType.DATE, StatColumnType.VALUE, StatColumnType.COMMENT])
    self.assertNotEqual(None, typed_stats_entry.date())
    self.assertNotEqual(None, typed_stats_entry.value())
    self.assertEqual(None, typed_stats_entry.id())
    self.assertNotEqual(None, typed_stats_entry.comment())

    typed_stats_entry = TypedStatsEntry(StatsEntry.from_str('06/04/2019;123;hello, world'),
                                        [StatColumnType.DATE, StatColumnType.VALUE, StatColumnType.ID])
    self.assertNotEqual(None, typed_stats_entry.date())
    self.assertNotEqual(None, typed_stats_entry.value())
    self.assertNotEqual(None, typed_stats_entry.id())
    self.assertEqual(None, typed_stats_entry.comment())
