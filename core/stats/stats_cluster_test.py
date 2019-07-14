import unittest
import math

from datetime import datetime

from core.stats.stats_cluster import StatsCluster
from core.stats.stat_column_type import StatColumnType
from core.stats.stats_metadata import StatsMetadata
from core.stats.stats_entry import StatsEntry

class StatsClusterTests(unittest.TestCase):
  def setUp(self):
    self.maxDiff = None

  def test_from_string(self):
    cluster = StatsCluster.from_str('date;value;id;comment\n13/05/2019;123;some_id;some comment')

    stats = cluster.entries()
    self.assertEqual(1, len(stats))
    types = cluster.metadata().types()
    self.assertEqual(4, len(types))

    self.assertEqual(StatColumnType.DATE, types[0])
    self.assertEqual(StatColumnType.VALUE, types[1])
    self.assertEqual(StatColumnType.ID, types[2])
    self.assertEqual(StatColumnType.COMMENT, types[3])

    self.assertEqual('13/05/2019', stats[0].columns[0])
    self.assertEqual('123', stats[0].columns[1])
    self.assertEqual('some_id', stats[0].columns[2])
    self.assertEqual('some comment', stats[0].columns[3])

  def test_to_string(self):
    cluster = StatsCluster(StatsMetadata.from_str('date;value;id;comment'),
                           [StatsEntry.from_str('13/05/2019;123;some_id;some comment')])
    self.assertEqual('date;value;id;comment\n13/05/2019;123;some_id;some comment', str(cluster))

  def test_from_string_with_complext_metadata(self):
    cluster_str = \
'''
28/05/2019;123;some_id321;some comment
===
- what: chart
  type: moving-average
  title: ma
  offset: 20
- what: chart
  title: periodic
  type: period
  unit: days
  unit-value: 7
- what: format
  value: date;value;id;comment
===
'''
    cluster = StatsCluster.from_str(cluster_str)
    stats = cluster.entries()
    self.assertEqual(1, len(stats))
    types = cluster.metadata().types()
    self.assertEqual(4, len(types))

    self.assertEqual(StatColumnType.DATE, types[0])
    self.assertEqual(StatColumnType.VALUE, types[1])
    self.assertEqual(StatColumnType.ID, types[2])
    self.assertEqual(StatColumnType.COMMENT, types[3])

    self.assertEqual('28/05/2019', stats[0].columns[0])
    self.assertEqual('123', stats[0].columns[1])
    self.assertEqual('some_id321', stats[0].columns[2])
    self.assertEqual('some comment', stats[0].columns[3])

    raw_metadata = cluster.metadata().raw_metadata()
    self.assertEqual(3, len(raw_metadata))
    self.assertEqual('chart', raw_metadata[0]['what'])
    self.assertEqual(4, len(raw_metadata[0]))
    self.assertEqual('chart', raw_metadata[1]['what'])
    self.assertEqual(5, len(raw_metadata[1]))
    self.assertEqual('format', raw_metadata[2]['what'])
    self.assertEqual(2, len(raw_metadata[2]))

  def test_to_string_with_complext_metadata(self):
    raw_metadata = []
    raw_metadata.append({'what':'chart', 'title':'title1', 'type':'moving-average', 'offset':2})
    raw_metadata.append({'what':'chart', 'title':'title2', 'type':'period', 'unit':'days', 'unit-value':7})
    raw_metadata.append({'what':'format', 'value':'date;value'})
    metadata = StatsMetadata([StatColumnType.DATE, StatColumnType.VALUE], None, raw_metadata)
    entries = [StatsEntry.from_str('28/05/2019;123')]

    cluster = StatsCluster(metadata, entries)

    expected_str = \
'''===
- what: chart
  title: title1
  type: moving-average
  offset: 2
- what: chart
  title: title2
  type: period
  unit: days
  unit-value: 7
- what: format
  value: date;value
===
28/05/2019;123'''
    self.assertEqual(expected_str, str(cluster))

  def test_types_in_metadata_used(self):
    cluster = StatsCluster.from_str('date;value;id;comment\n13/05/2019;123;some_id;some comment')

    self.assertEqual(StatColumnType.DATE, cluster.type_at(0))
    self.assertEqual(StatColumnType.VALUE, cluster.type_at(1))
    self.assertEqual(StatColumnType.ID, cluster.type_at(2))
    self.assertEqual(StatColumnType.COMMENT, cluster.type_at(3))

    self.assertTrue(isinstance(cluster.typed_entries()[0].at(0), datetime))
    self.assertEqual(datetime.strptime('13/05/2019', '%d/%m/%Y'), cluster.typed_entries()[0].at(0))

    self.assertTrue(isinstance(cluster.typed_entries()[0].at(1), float))
    self.assertTrue(math.isclose(cluster.typed_entries()[0].at(1), 123, abs_tol=0.1))

    self.assertTrue(isinstance(cluster.typed_entries()[0].at(2), str))
    self.assertEqual('some_id', cluster.typed_entries()[0].at(2))

    self.assertTrue(isinstance(cluster.typed_entries()[0].at(3), str))
    self.assertEqual('some comment', cluster.typed_entries()[0].at(3))

  def test_can_collapse_clusters(self):
    stats_entries = [StatsEntry.from_str('06/04/2019;1;hello'),
                     StatsEntry.from_str('07/04/2019;1;world'),
                     StatsEntry.from_str('06/04/2019;1;hello'),
                     StatsEntry.from_str('08/04/2019;1;world'),
                     StatsEntry.from_str('07/04/2019;1;world')]
    metadata = StatsMetadata([StatColumnType.DATE, StatColumnType.VALUE, StatColumnType.ID])

    stats_cluster = StatsCluster(metadata, stats_entries).collapse()
    self.assertEqual(3, len(stats_cluster.entries()))
    self.assertTrue(StatsEntry.from_str('06/04/2019;2;hello') in stats_cluster.entries())
    self.assertTrue(StatsEntry.from_str('07/04/2019;2;world') in stats_cluster.entries())
    self.assertTrue(StatsEntry.from_str('08/04/2019;1;world') in stats_cluster.entries())

  def test_collapsing_sorts_entries_by_date(self):
    stats_entries = [StatsEntry.from_str('06/04/2019;1;hello'),
                     StatsEntry.from_str('05/04/2019;1;world'),
                     StatsEntry.from_str('04/04/2019;1;!')]
    metadata = StatsMetadata([StatColumnType.DATE, StatColumnType.VALUE, StatColumnType.ID])

    stats_cluster = StatsCluster(metadata, stats_entries).collapse()

    self.assertEqual(StatsEntry.from_str('06/04/2019;1;hello'), stats_cluster.entries()[0])
    self.assertEqual(StatsEntry.from_str('05/04/2019;1;world'), stats_cluster.entries()[1])
    self.assertEqual(StatsEntry.from_str('04/04/2019;1;!'), stats_cluster.entries()[2])

  def test_can_merge_2_clusters(self):
    entries1 = [StatsEntry.from_str('06/04/2019;1;descr1'),
                StatsEntry.from_str('07/04/2019;1;descr2'),
                StatsEntry.from_str('08/04/2019;1;descr3')]
    entries2 = [StatsEntry.from_str('05/04/2019;2;descr1'),
                StatsEntry.from_str('07/04/2019;3;descr4'),
                StatsEntry.from_str('09/04/2019;4;descr3')]
    metadata = StatsMetadata([StatColumnType.DATE, StatColumnType.VALUE, StatColumnType.ID])

    cluster1 = StatsCluster(metadata, entries1)
    cluster2 = StatsCluster(metadata, entries2)

    merged_cluster = cluster1.merge(cluster2, prioritized=cluster1)
    self.assertEqual(6, len(merged_cluster.entries()))
    self.assertTrue(StatsEntry.from_str('05/04/2019;2;descr1') in merged_cluster.entries())
    self.assertTrue(StatsEntry.from_str('06/04/2019;1;descr1') in merged_cluster.entries())
    self.assertTrue(StatsEntry.from_str('07/04/2019;1;descr2') in merged_cluster.entries())
    self.assertTrue(StatsEntry.from_str('07/04/2019;3;descr4') in merged_cluster.entries())
    self.assertTrue(StatsEntry.from_str('08/04/2019;1;descr3') in merged_cluster.entries())
    self.assertTrue(StatsEntry.from_str('09/04/2019;4;descr3') in merged_cluster.entries())

  def test_can_choose_prioritized_cluster1_list_when_merging(self):
    entries1 = [StatsEntry.from_str('06/04/2019;1;descr1'),
                StatsEntry.from_str('07/04/2019;1;descr2'),
                StatsEntry.from_str('08/04/2019;1;descr3')]
    entries2 = [StatsEntry.from_str('05/04/2019;2;descr1'),
                StatsEntry.from_str('07/04/2019;3;descr2'),
                StatsEntry.from_str('09/04/2019;4;descr3')]
    metadata = StatsMetadata([StatColumnType.DATE, StatColumnType.VALUE, StatColumnType.ID])

    cluster1 = StatsCluster(metadata, entries1)
    cluster2 = StatsCluster(metadata, entries2)
    merged_cluster = cluster1.merge(cluster2, prioritized=cluster1)

    self.assertEqual(5, len(merged_cluster.entries()))
    self.assertTrue(StatsEntry.from_str('05/04/2019;2;descr1') in merged_cluster.entries())
    self.assertTrue(StatsEntry.from_str('06/04/2019;1;descr1') in merged_cluster.entries())
    self.assertTrue(StatsEntry.from_str('07/04/2019;1;descr2') in merged_cluster.entries())
    self.assertTrue(StatsEntry.from_str('08/04/2019;1;descr3') in merged_cluster.entries())
    self.assertTrue(StatsEntry.from_str('09/04/2019;4;descr3') in merged_cluster.entries())

  def test_can_choose_prioritized_cluster2_list_when_merging(self):
    entries1 = [StatsEntry.from_str('06/04/2019;1;descr1'),
                StatsEntry.from_str('07/04/2019;1;descr2'),
                StatsEntry.from_str('08/04/2019;1;descr3')]
    entries2 = [StatsEntry.from_str('05/04/2019;2;descr1'),
                StatsEntry.from_str('07/04/2019;3;descr2'),
                StatsEntry.from_str('09/04/2019;4;descr3')]
    metadata = StatsMetadata([StatColumnType.DATE, StatColumnType.VALUE, StatColumnType.ID])

    cluster1 = StatsCluster(metadata, entries1)
    cluster2 = StatsCluster(metadata, entries2)
    merged_cluster = cluster1.merge(cluster2, prioritized=cluster2)

    self.assertEqual(5, len(merged_cluster.entries()))
    self.assertTrue(StatsEntry.from_str('05/04/2019;2;descr1') in merged_cluster.entries())
    self.assertTrue(StatsEntry.from_str('06/04/2019;1;descr1') in merged_cluster.entries())
    self.assertTrue(StatsEntry.from_str('07/04/2019;3;descr2') in merged_cluster.entries())
    self.assertTrue(StatsEntry.from_str('08/04/2019;1;descr3') in merged_cluster.entries())
    self.assertTrue(StatsEntry.from_str('09/04/2019;4;descr3') in merged_cluster.entries())

  def test_merging_sorts_entries_by_date(self):
    entries1 = [StatsEntry.from_str('07/04/2019;1;descr1'),
                StatsEntry.from_str('05/04/2019;1;descr2')]

    entries2 = [StatsEntry.from_str('08/04/2019;2;descr1'),
                StatsEntry.from_str('06/04/2019;3;descr4')]

    metadata = StatsMetadata([StatColumnType.DATE, StatColumnType.VALUE, StatColumnType.ID])

    cluster1 = StatsCluster(metadata, entries1)
    cluster2 = StatsCluster(metadata, entries2)
    merged_cluster = cluster1.merge(cluster2, prioritized=cluster2)

    self.assertEqual(4, len(merged_cluster.entries()))
    self.assertEqual(merged_cluster.entries()[0], StatsEntry.from_str('08/04/2019;2;descr1'))
    self.assertEqual(merged_cluster.entries()[1], StatsEntry.from_str('07/04/2019;1;descr1'))
    self.assertEqual(merged_cluster.entries()[2], StatsEntry.from_str('06/04/2019;3;descr4'))
    self.assertEqual(merged_cluster.entries()[3], StatsEntry.from_str('05/04/2019;1;descr2'))

  def test_merge_throws_if_clusters_not_collapsed(self):
    entries1 = [StatsEntry.from_str('06/04/2019;1;descr1'),
                StatsEntry.from_str('06/04/2019;1;descr1')]

    entries2 = [StatsEntry.from_str('07/04/2019;2;descr2'),
                StatsEntry.from_str('07/04/2019;3;descr2')]

    metadata = StatsMetadata([StatColumnType.DATE, StatColumnType.VALUE, StatColumnType.ID])
    cluster1 = StatsCluster(metadata, entries1)
    cluster2 = StatsCluster(metadata, entries2)

    exception_caught1 = False
    try:
        cluster3 = StatsCluster(metadata, [StatsEntry.from_str('07/04/2019;3;descr2')])
        cluster1.merge(cluster3, prioritized=cluster1)
    except:
        exception_caught1 = True
    self.assertTrue(exception_caught1)

    exception_caught2 = False
    try:
        cluster3 = StatsCluster(metadata, [StatsEntry.from_str('06/04/2019;1;descr1')])
        cluster2.merge(cluster3, prioritized=cluster2)
    except:
        exception_caught2 = True
    self.assertTrue(exception_caught2)
