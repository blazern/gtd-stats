import unittest
import core.test_utils as test_utils

from core.stats_metadata import StatsMetadata
from core.stats_metadata import StatColumnType
from core.chart_appearance import *

class StatsMetadataTests(unittest.TestCase):
  def test_parse_simple_str(self):
    metadata_str = 'date;value;id;comment'
    metadata = StatsMetadata.from_str(metadata_str)

    types = metadata.types()
    self.assertEqual(4, len(types))

    self.assertEqual(types[0], StatColumnType.DATE)
    self.assertEqual(types[1], StatColumnType.VALUE)
    self.assertEqual(types[2], StatColumnType.ID)
    self.assertEqual(types[3], StatColumnType.COMMENT)

  def test_to_simple_string(self):
    metadata_str = 'date;value;id;comment'
    metadata = StatsMetadata.from_str(metadata_str)
    self.assertEqual(metadata_str, str(metadata))

  def test_parse_simple_str_with_extras(self):
    metadata_str = 'date;value:atata'
    metadata = StatsMetadata.from_str(metadata_str)

    types = metadata.types()
    self.assertEqual(2, len(types))
    self.assertEqual(types[0], StatColumnType.DATE)
    self.assertEqual(types[1], StatColumnType.VALUE)

    types_extras = metadata.types_extras()
    self.assertEqual(2, len(types_extras))
    self.assertEqual(types_extras[0], None)
    self.assertEqual(types_extras[1], 'atata')    

  def test_to_simple_string_with_extras(self):
    metadata_str = 'date;value:atata;id;comment'
    metadata = StatsMetadata.from_str(metadata_str)
    self.assertEqual(metadata_str, str(metadata))

  def test_find_simple_string_position(self):
    string =\
'''\
date;value
25/05/2019;123
'''
    pos_start, pos_end = StatsMetadata.find_str_position(string)
    self.assertEqual(0, pos_start)
    self.assertEqual(10, pos_end)

  def test_find_complex_string_position_at_start(self):
    string =\
'''\
===
- what: chart
  title: my name 1
  types:
    - type: moving-average
    - type: period
      unit: days
      unit-value: 7
- what: chart
  title: monts!
  type: period
  unit: months
  unit-value: 1
- what: chart
  title: pretty average!
  type: moving-average
- what: format
  value: date;id
===
25/05/2019;123
'''
    pos_start, pos_end = StatsMetadata.find_str_position(string)
    self.assertEqual(0, pos_start)
    self.assertEqual(302, pos_end)

  def test_find_complex_string_position_at_end(self):
    string =\
'''\
25/05/2019;123
===
- what: chart
  title: my name 1
  types:
    - type: moving-average
    - type: period
      unit: days
      unit-value: 7
- what: chart
  title: monts!
  type: period
  unit: months
  unit-value: 1
- what: chart
  title: pretty average!
  type: moving-average
- what: format
  value: date;id
===
'''
    pos_start, pos_end = StatsMetadata.find_str_position(string)
    self.assertEqual(15, pos_start)
    self.assertEqual(318, pos_end)

  def test_complex_metadata_string_parsing(self):
    string =\
'''\
===
- what: chart
  title: my name 1
  types:
  - type: moving-average
    offset: 3
  - type: period
    unit: days
    unit-value: 7
- what: chart
  title: months!
  type: period
  unit: months
  unit-value: 1
- what: chart
  title: pretty average!
  type: moving-average
  offset: 6
- what: format
  value: date;id
===
'''
    metadata = StatsMetadata.from_str(string)

    types = metadata.types()
    self.assertEqual(2, len(types))
    self.assertEqual(types[0], StatColumnType.DATE)
    self.assertEqual(types[1], StatColumnType.ID)

    appearances = metadata.chart_appearances()
    self.assertEqual(3, len(appearances))

    appearance1 = appearances[0]
    self.assertEqual('my name 1', appearance1.title)
    self.assertEqual(2, len(appearance1.modifiers))
    self.assertEqual(MovingAverageChartAppearanceModifier, type(appearance1.modifiers[0]))
    self.assertEqual(3, appearance1.modifiers[0].offset)
    self.assertEqual(PeriodChartAppearanceModifier, type(appearance1.modifiers[1]))
    self.assertEqual(PeriodChartAppearanceModifier.Unit.DAY, appearance1.modifiers[1].time_unit)
    self.assertEqual(7, appearance1.modifiers[1].time_period_size)

    appearance2 = appearances[1]
    self.assertEqual('months!', appearance2.title)
    self.assertEqual(1, len(appearance2.modifiers))
    self.assertEqual(PeriodChartAppearanceModifier, type(appearance2.modifiers[0]))
    self.assertEqual(PeriodChartAppearanceModifier.Unit.MONTH, appearance2.modifiers[0].time_unit)
    self.assertEqual(1, appearance2.modifiers[0].time_period_size)

    appearance3 = appearances[2]
    self.assertEqual('pretty average!', appearance3.title)
    self.assertEqual(1, len(appearance3.modifiers))
    self.assertEqual(MovingAverageChartAppearanceModifier, type(appearance3.modifiers[0]))
    self.assertEqual(6, appearance3.modifiers[0].offset)

  def test_complex_metadata_string_encoding(self):
    chart_appearances = []
    chart_appearances.append(ChartAppearance('title1', [MovingAverageChartAppearanceModifier(2)]))
    chart_appearances.append(ChartAppearance('title2',
                                            [MovingAverageChartAppearanceModifier(3),
                                             PeriodChartAppearanceModifier(PeriodChartAppearanceModifier.Unit.YEAR, 2)]))
    chart_appearances.append(ChartAppearance('title3', [PeriodChartAppearanceModifier(PeriodChartAppearanceModifier.Unit.DAY, 7)]))
    metadata = StatsMetadata([StatColumnType.DATE, StatColumnType.VALUE], None, chart_appearances)

    expected_str =\
'''
===
- what: chart
  title: title1
  type: moving-average
  offset: 2
- what: chart
  title: title2
  types:
  - type: moving-average
    offset: 3
  - type: period
    unit: years
    unit-value: 2
- what: chart
  title: title3
  type: period
  unit: days
  unit-value: 7
- what: format
  value: date;value
===
'''
    self.maxDiff = None
    self.assertEqual(expected_str.strip(), str(metadata))
