class Coordinate:
  """Initializes the coordinate class."""
  def __init__(self, x, y):
    self.x = x
    self.y = y
  

  def __str__(self):
    """Returns an ordered pair in string form."""
    return '(' + str(self.x) + ', ' + str(self.y) + ')'
  
  
  def __eq__(self, other):
    """Returns True if the x & y member variables are equal, False otherwise."""
    return self.x == other.x and self.y == other.y


  def __hash__(self):
    """Returns a hash representation of a coordinate."""
    return (self.x + 1) * 100000 + self.y
