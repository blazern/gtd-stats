import unittest
import core.test_utils as test_utils

from core.stats_metadata import StatsMetadata
from core.stats_metadata import StatColumnType

class StatsMetadataTests(unittest.TestCase):
  def test_parse_str(self):
    metadata_str = 'date;value;id;comment'
    metadata = StatsMetadata.from_str(metadata_str)

    types = metadata.types()
    self.assertEqual(4, len(types))

    self.assertEqual(types[0], StatColumnType.DATE)
    self.assertEqual(types[1], StatColumnType.VALUE)
    self.assertEqual(types[2], StatColumnType.ID)
    self.assertEqual(types[3], StatColumnType.COMMENT)

  def test_to_string(self):
    metadata_str = 'date;value;id;comment'
    metadata = StatsMetadata.from_str(metadata_str)
    self.assertEqual(metadata_str, str(metadata))