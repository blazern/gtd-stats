import unittest

from datetime import datetime

from core.stats_entry import StatsEntry

class StatsEntryTests(unittest.TestCase):
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

  def test_can_merge_2_entries_lists(self):
    entries1 = [StatsEntry.from_str('06/04/2019;1;descr1'),
                StatsEntry.from_str('07/04/2019;1;descr2'),
                StatsEntry.from_str('08/04/2019;1;descr3')]

    entries2 = [StatsEntry.from_str('05/04/2019;2;descr1'),
                StatsEntry.from_str('07/04/2019;3;descr4'),
                StatsEntry.from_str('09/04/2019;4;descr3')]

    merged_entries = StatsEntry.merge(entries1, entries2, prioritized=entries1)
    self.assertEqual(6, len(merged_entries))
    self.assertTrue(StatsEntry.from_str('05/04/2019;2;descr1') in merged_entries)
    self.assertTrue(StatsEntry.from_str('06/04/2019;1;descr1') in merged_entries)
    self.assertTrue(StatsEntry.from_str('07/04/2019;1;descr2') in merged_entries)
    self.assertTrue(StatsEntry.from_str('07/04/2019;3;descr4') in merged_entries)
    self.assertTrue(StatsEntry.from_str('08/04/2019;1;descr3') in merged_entries)
    self.assertTrue(StatsEntry.from_str('09/04/2019;4;descr3') in merged_entries)

  def test_can_choose_prioritized_entries1_list_when_merging(self):
    entries1 = [StatsEntry.from_str('06/04/2019;1;descr1'),
                StatsEntry.from_str('07/04/2019;1;descr2'),
                StatsEntry.from_str('08/04/2019;1;descr3')]

    entries2 = [StatsEntry.from_str('05/04/2019;2;descr1'),
                StatsEntry.from_str('07/04/2019;3;descr2'),
                StatsEntry.from_str('09/04/2019;4;descr3')]

    merged_entries = StatsEntry.merge(entries1, entries2, prioritized=entries1)
    self.assertEqual(5, len(merged_entries))
    self.assertTrue(StatsEntry.from_str('05/04/2019;2;descr1') in merged_entries)
    self.assertTrue(StatsEntry.from_str('06/04/2019;1;descr1') in merged_entries)
    self.assertTrue(StatsEntry.from_str('07/04/2019;1;descr2') in merged_entries)
    self.assertTrue(StatsEntry.from_str('08/04/2019;1;descr3') in merged_entries)
    self.assertTrue(StatsEntry.from_str('09/04/2019;4;descr3') in merged_entries)

  def test_can_choose_prioritized_entries2_list_when_merging(self):
    entries1 = [StatsEntry.from_str('06/04/2019;1;descr1'),
                StatsEntry.from_str('07/04/2019;1;descr2'),
                StatsEntry.from_str('08/04/2019;1;descr3')]

    entries2 = [StatsEntry.from_str('05/04/2019;2;descr1'),
                StatsEntry.from_str('07/04/2019;3;descr2'),
                StatsEntry.from_str('09/04/2019;4;descr3')]

    merged_entries = StatsEntry.merge(entries1, entries2, prioritized=entries2)
    self.assertEqual(5, len(merged_entries))
    self.assertTrue(StatsEntry.from_str('05/04/2019;2;descr1') in merged_entries)
    self.assertTrue(StatsEntry.from_str('06/04/2019;1;descr1') in merged_entries)
    self.assertTrue(StatsEntry.from_str('07/04/2019;3;descr2') in merged_entries)
    self.assertTrue(StatsEntry.from_str('08/04/2019;1;descr3') in merged_entries)
    self.assertTrue(StatsEntry.from_str('09/04/2019;4;descr3') in merged_entries)

  def test_merging_sorts_entries_by_date(self):
    entries1 = [StatsEntry.from_str('07/04/2019;1;descr1'),
                StatsEntry.from_str('05/04/2019;1;descr2')]

    entries2 = [StatsEntry.from_str('08/04/2019;2;descr1'),
                StatsEntry.from_str('06/04/2019;3;descr4')]

    merged_entries = StatsEntry.merge(entries1, entries2, prioritized=entries1)
    self.assertEqual(4, len(merged_entries))
    self.assertEqual(merged_entries[0], StatsEntry.from_str('05/04/2019;1;descr2'))
    self.assertEqual(merged_entries[1], StatsEntry.from_str('06/04/2019;3;descr4'))
    self.assertEqual(merged_entries[2], StatsEntry.from_str('07/04/2019;1;descr1'))
    self.assertEqual(merged_entries[3], StatsEntry.from_str('08/04/2019;2;descr1'))

  def test_merge_throws_if_lists_not_collapsed(self):
    entries1 = [StatsEntry.from_str('06/04/2019;1;descr1'),
                StatsEntry.from_str('06/04/2019;1;descr1')]

    entries2 = [StatsEntry.from_str('07/04/2019;2;descr2'),
                StatsEntry.from_str('07/04/2019;3;descr2')]

    exception_caught1 = False
    try:
        StatsEntry.merge(entries1, [StatsEntry.from_str('07/04/2019;3;descr2')], prioritized=entries1)
    except:
        exception_caught1 = True
    self.assertTrue(exception_caught1)

    exception_caught2 = False
    try:
        StatsEntry.merge([StatsEntry.from_str('06/04/2019;1;descr1')], entries2, prioritized=entries2)
    except:
        exception_caught2 = True
    self.assertTrue(exception_caught2)
