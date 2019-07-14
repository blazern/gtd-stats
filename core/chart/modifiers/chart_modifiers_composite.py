from core.chart.modifiers.chart_modifier import *

class ChartModifiersComposite(ChartModifier):
  def __init__(self, title, modifiers):
    types = set()
    for modifier in modifiers:
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
  def convert_coords(self, coords_x, coords_y):
    if len(coords_x) != len(coords_y):
      raise ValueError('Lengths of x and y coords is different: {}, {}'.format(coords_x, coords_y))
    converted_x = coords_x
    converted_y = coords_y
    for modifier in self._modifiers:
      converted_x, converted_y = modifier.convert_coords(converted_x, converted_y)
    return converted_x, converted_y

  # Override
  def convert_stats(self, stats_entries):
    for modifier in self._modifiers:
      stats_entries = modifier.convert_stats(stats_entries)
    return stats_entries

  # Override
  def title(self):
    titles = [self._title]
    for modifier in modifiers:
      if modifier.title() is not None:
        titles.append(modifier.title())
    return '_'.join(titles)