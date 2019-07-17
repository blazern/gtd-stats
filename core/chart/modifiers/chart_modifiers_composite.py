from core.chart.modifiers.chart_modifier import *

class ChartModifiersComposite(ChartModifier):
  def __init__(self, title, modifiers):
    types = set()
    for modifier in modifiers:
      if modifier.multiple_modifiers_of_type_allowed():
        continue
      if type(modifier) in types:
        raise ValueError('Can\' have more than 1 modifier of same types. Duplicating modifier: {}'.format(type(modifier)))
      types.add(type(modifier))
    self.title = title
    self.modifiers = modifiers
    self._modifiers = modifiers
    self._title = title

  def modifiers(self):
    return self.modifiers

  # Override
  def convert_lines(self, lines):
    for modifier in self._modifiers:
      lines = modifier.convert_lines(lines)
    return lines

  # Override
  def convert_stats(self, typed_entries, metadata):
    for modifier in self._modifiers:
      typed_entries, metadata = modifier.convert_stats(typed_entries, metadata)
    return typed_entries, metadata

  # Override
  def title(self):
    titles = [self._title]
    for modifier in modifiers:
      if modifier.title() is not None:
        titles.append(modifier.title())
    return '_'.join(titles)