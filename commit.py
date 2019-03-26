class Commit:
  def __init__(self, sha1, date, author, msg):
    self.sha1 = sha1
    self.date = date
    self.author = author
    self.msg = msg