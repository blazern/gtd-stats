import unittest

from datetime import datetime

from core.git.commit import Commit
from core.stats.stats_entry import StatsEntry
from core.stats.typed_stats_entry import TypedStatsEntry

class CommitTests(unittest.TestCase):
  def test_can_convert_into_stats_entry(self):
    commit = Commit('72bc426f2a653d45485c3ae415e0186785265c89',
                    datetime.strptime('2019-04-06', '%Y-%m-%d'),
                    'blazern',
                    'Aren\'t you nosy!')

    stats_entry = commit.to_stats_entry()

    self.assertTrue(isinstance(stats_entry, TypedStatsEntry))
    self.assertEqual(1, stats_entry.value()) # 1 commit
    self.assertEqual(commit.date, stats_entry.date())
    self.assertEqual(commit.author, stats_entry.id())
