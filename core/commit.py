from core.stat_column_type import StatColumnType
from core.stats_entry import StatsEntry
from core.typed_stats_entry import TypedStatsEntry

class Commit:
  def __init__(self, sha1, date, author, msg):
    self.sha1 = sha1
    self.date = date
    self.author = author
    self.msg = msg

  def to_stats_entry(self):
    return TypedStatsEntry.from_stats([StatColumnType.DATE, StatColumnType.VALUE, StatColumnType.ID],
                                      [self.date,     1,              self.author])
