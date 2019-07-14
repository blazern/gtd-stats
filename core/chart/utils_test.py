import unittest

from core.stats.stats_metadata import StatsMetadata
from core.chart.utils import *
from core.chart.modifiers.chart_modifiers_composite import *
from core.chart.modifiers.moving_average_chart_modifier import *
from core.chart.modifiers.period_chart_modifier import *

class ChartUtilsTests(unittest.TestCase):
  def setUp(self):
    self.maxDiff = None

  def test_appearances_extracted_correctly(self):
    metadata_str = \
'''
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
- what: chart
  title: combo
  types:
  - what: chart
    type: moving-average
    offset: 2
  - what: chart
    type: period
    unit: days
    unit-value: 3
- what: format
  value: date;value;id;comment
===
'''
    metadata = StatsMetadata.from_str(metadata_str)

    appearances = extract_chart_modifiers_from_stats_metadata(metadata)
    self.assertEqual(3, len(appearances))

    appearance1 = appearances[0]
    self.assertEqual('ma', appearance1.title)
    self.assertEqual(1, len(appearance1.modifiers))
    self.assertEqual(MovingAverageChartModifier, type(appearance1.modifiers[0]))
    self.assertEqual(20, appearance1.modifiers[0].offset)

    appearance2 = appearances[1]
    self.assertEqual('periodic', appearance2.title)
    self.assertEqual(1, len(appearance2.modifiers))
    self.assertEqual(PeriodChartModifier, type(appearance2.modifiers[0]))
    self.assertEqual(PeriodChartModifier.Unit.DAY, appearance2.modifiers[0].time_unit)
    self.assertEqual(7, appearance2.modifiers[0].time_period_size)

    appearance3 = appearances[2]
    self.assertEqual('combo', appearance3.title)
    self.assertEqual(2, len(appearance3.modifiers))
    self.assertEqual(MovingAverageChartModifier, type(appearance3.modifiers[0]))
    self.assertEqual(2, appearance3.modifiers[0].offset)
    self.assertEqual(PeriodChartModifier, type(appearance3.modifiers[1]))
    self.assertEqual(PeriodChartModifier.Unit.DAY, appearance3.modifiers[1].time_unit)
    self.assertEqual(3, appearance3.modifiers[1].time_period_size)