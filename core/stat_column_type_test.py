import unittest

from core.stat_column_type import StatColumnType

class StatColumnTypeTests(unittest.TestCase):
  def test_converts_to_str(self):
    # Making sure no types are forgotten
    self.assertEqual(4, len(list(StatColumnType)))

    self.assertEqual('date', str(StatColumnType.DATE))
    self.assertEqual('value', str(StatColumnType.VALUE))
    self.assertEqual('id', str(StatColumnType.ID))
    self.assertEqual('comment', str(StatColumnType.COMMENT))

  def test_constructs_from_str(self):
    # Making sure no types are forgotten
    self.assertEqual(4, len(list(StatColumnType)))

    self.assertEqual(StatColumnType.DATE, StatColumnType.from_str('date'))
    self.assertEqual(StatColumnType.VALUE, StatColumnType.from_str('value'))
    self.assertEqual(StatColumnType.ID, StatColumnType.from_str('id'))
    self.assertEqual(StatColumnType.COMMENT, StatColumnType.from_str('comment'))
