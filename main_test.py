import unittest

from main import extract_author_aliases_from

class MainTests(unittest.TestCase):
  def test_extracts_authors_aliases(self):
    aliases = extract_author_aliases_from('author1:alias1;author1:alias2;author2:alias3')
    self.assertEqual(2, len(aliases))
    self.assertTrue('author1' in aliases)
    self.assertTrue('author2' in aliases)
    
    self.assertEqual(2, len(aliases['author1']))
    self.assertTrue('alias1' in aliases['author1'])
    self.assertTrue('alias2' in aliases['author1'])

    self.assertEqual(1, len(aliases['author2']))
    self.assertTrue('alias3' in aliases['author2'])

  def test_cannot_use_author_as_alias(self):
    exception_caught = False
    try:
      extract_author_aliases_from('author1:alias1;author2:author1')
    except:
      exception_caught = True
    self.assertTrue(exception_caught)

  def test_cannot_mention_alias_twice(self):
    exception_caught = False
    try:
      extract_author_aliases_from('author1:alias1;author1:alias1')
    except:
      exception_caught = True
    self.assertTrue(exception_caught)

  def test_cannot_use_empty_author(self):
    exception_caught = False
    try:
      extract_author_aliases_from(':alias1')
    except:
      exception_caught = True
    self.assertTrue(exception_caught)

  def test_cannot_use_empty_alias(self):
    exception_caught = False
    try:
      extract_author_aliases_from('author1:')
    except:
      exception_caught = True
    self.assertTrue(exception_caught)