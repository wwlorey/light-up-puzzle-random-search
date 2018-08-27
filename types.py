from enum import Enum


class Error(Exception):
  def __init__(self, color, coord):
    self.color = color
    self.coord = coord
    self.message = '\nError: \tCould not place BULB on ' + ('BLACK' if self.color == Color.BLACK else 'WHITE') + ' square at coord (' + str(self.coord.x) + ', ' + str(self.coord.y) + ').\n\t'


class SquareError(Error):
  def __init__(self, color, coord):
    Error.__init__(self, color, coord)
    self.message += 'BULBs can only be placed on WHITE squares.\n' 


class ShineError(Error):
  def __init__(self, color, coord):
    Error.__init__(self, color, coord)
    self.message += 'BULBs can only be placed where light does not already shine.\n'


class BulbError(Error):
  def __init__(self, color, coord):
    Error.__init__(color, coord)
    self.message += 'There is already a BULB on that square.\n'


class Color(Enum):
  BLACK = 0
  WHITE = 1


class Coordinate:
  def __init__(self, x, y):
    self.x = x
    self.y = y
  
  def __str__(self):
    """Returns an ordered pair in string form."""
    return '(' + str(self.x) + ', ' + str(self.y) + ')'


class Square:
  def __init__(self, color):
    self.color = color


class BlackSquare(Square):
  def __init__(self, adj_value):
    Square.__init__(self, Color.BLACK)
    self.adj_value = adj_value
  
  def __str__(self):
    """Returns the adjacency value in string form."""
    return str(self.adj_value)


class WhiteSquare(Square):
  def __init__(self):
    Square.__init__(self, Color.WHITE)
    self.has_shine = False
    self.has_bulb = False

  def __str__(self):
    """Returns a string symbol representing what is on the square."""
    if self.has_bulb:
      return '!'

    if self.has_shine:
      return '*'

    return '_'


class Board():
  def __init__(self, input_file_name):
    input_file = open(input_file_name, 'r')

    # Read line 0 (number of columns)
    self.num_cols = int(input_file.readline())

    # Read line 1 (number of rows)
    self.num_rows = int(input_file.readline())

    # Initialize board with all white squares
    self.board = [ [ WhiteSquare() for row in range(self.num_rows) ] for col in range(self.num_cols) ]

    # Read line 2 to EoF (coordinates of black squares and their adjacency values)
    for row_index, row_str in enumerate(input_file):
      line_list = [int(i) for i in row_str.split()]
      black_square_col = line_list[0] - 1
      black_square_row = line_list[1] - 1
      adj_value = line_list[2]

      self.board[black_square_row][black_square_col] = BlackSquare(adj_value)
    
    # Generate a coordinate versions of the board
    self.coord_board = []

    for x in range(self.num_rows):
      coord_list = []
      for y in range(self.num_cols):
        coord_list.append(Coordinate(x, y))
      self.coord_board.append(coord_list)
    
    self.transpose_coord_board = [list(l) for l in zip(*self.coord_board)]
  
  def __str__(self):
    """Returns the string representation of every square in the board"""
    ret = ''

    for row in self.board:
      for elem in row:
        ret += str(elem) + ' '

      ret += '\n'
    
    return ret
  
  def put_bulb(self, coord):
    """Attempts to place a bulb at coord position on self.board.

    Returns True on success, False on fail.
    Logs error message to log file, if applicable.
    """
    square = self.board[coord.x][coord.y]

    if square.color == Color.WHITE and not square.has_shine and not square.has_bulb and self.update_shine(coord):
      self.board[coord.x][coord.y].has_bulb = True
      return True

    if square.color == Color.BLACK:
      log_file.write(SquareError(square.color, coord).message)
    
    elif square.has_shine:
      log_file.write(ShineError(square.color, coord).message)
    
    elif square.has_bulb:
      log_file.write(BulbError(square.color, coord).message)
    
    return False

  def update_shine(self, coord):
    """Sets has_shine flag for all squares horizontally and vertically
    adjacent to coord.

    Returns True if the shine does not fall on other bulbs, False otherwise.
    Only updates self.board if shine does not fall on other bulbs.
    """

    class ShineInfo(Enum):
      NO_ERROR           = 0
      FOUND_BLACK_SQUARE = 1
      FOUND_BULB         = 2

    def check_update_square_shine(board, coord):
      """Determines if a square can be safely shined on.

      Returns a ShineInfo flag. 
      """
      square = board[coord.x][coord.y]

      if square.color == Color.WHITE:
        if square.has_bulb:
          return ShineInfo.FOUND_BULB
        else:
          square.has_shine = True
          return ShineInfo.NO_ERROR
      
      return ShineInfo.FOUND_BLACK_SQUARE
    
    # Temporary board so changes are not permanent until safe shining is ensured
    tmp_board = self.board

    # Create a list of adjacency lists - used for determining where the bulb shines
    adj_coord_lists = []

    adj_coord_lists.append(self.coord_board[coord.x][:coord.y][::-1])           # Row from this column to the left
    adj_coord_lists.append(self.coord_board[coord.x][coord.y + 1:])             # Row from this column to the right
    adj_coord_lists.append(self.transpose_coord_board[coord.y][:coord.x][::-1]) # Column from this row up
    adj_coord_lists.append(self.transpose_coord_board[coord.y][coord.x + 1:])   # Column from this row down

    for coord_list in adj_coord_lists:
      for coord in coord_list:
        result = check_update_square_shine(tmp_board, coord)
    
        if result == ShineInfo.FOUND_BULB:
          return False
        elif result == ShineInfo.FOUND_BLACK_SQUARE:
          break

    # Copy changes to the real board
    self.board = tmp_board

    return True
      
  
log_file = open('log.txt', 'w')

b = Board('input.txt')

for x in range(b.num_rows):
  for y in range(b.num_cols):
    c = Coordinate(x, y)
    print('Success' if b.put_bulb(c) else 'Fail')
    print(c)
    print(b)
    print('\n\n')
