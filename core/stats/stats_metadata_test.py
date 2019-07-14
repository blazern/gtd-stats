import unittest
import core.test_utils as test_utils

from core.stats.stats_metadata import StatsMetadata
from core.stats.stats_metadata import StatColumnType
from core.chart.chart_appearance import *

class StatsMetadataTests(unittest.TestCase):
  def setUp(self):
    self.maxDiff = None

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

    raw_metadata = metadata.raw_metadata()
    self.assertEqual(2, len(raw_metadata))

    self.assertEqual('chart', raw_metadata[0]['what'])
    self.assertEqual('pretty average!', raw_metadata[0]['title'])
    self.assertEqual('moving-average', raw_metadata[0]['type'])
    self.assertEqual(6, raw_metadata[0]['offset'])

    self.assertEqual('format', raw_metadata[1]['what'])
    self.assertEqual('date;id', raw_metadata[1]['value'])
