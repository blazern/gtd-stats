from stats_entry import StatsEntry

class Commit:
  def __init__(self, sha1, date, author, msg):
    self.sha1 = sha1
    self.date = date
    self.author = author
    self.msg = msg

  def to_stats_entry(self):
    return StatsEntry(date=self.date, value=1, description=self.author)
