class Commit:
  def __init__(self, sha1, timestamp, author, msg):
    self.sha1 = sha1
    self.timestamp = timestamp
    self.author = author
    self.msg = msg