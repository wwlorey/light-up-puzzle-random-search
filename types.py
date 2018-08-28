from enum import Enum
import json


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
    Error.__init__(self, color, coord)
    self.message += 'There is already a BULB on that square.\n'


class Color(Enum):
  BLACK = 0
  WHITE = 1


class BlackSquareAdjValue(Enum):
  NONE_ADJ      = 0
  ONE_ADJ       = 1
  TWO_ADJ       = 2
  THREE_ADJ     = 3
  FOUR_ADJ      = 4
  DONT_CARE_ADJ = 5


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

    self.num_empty_white_squares = self.num_rows * self.num_cols

    # Read line 2 to EoF (coordinates of black squares and their adjacency values)
    for row_index, row_str in enumerate(input_file):
      line_list = [int(i) for i in row_str.split()]
      black_square_col = line_list[0] - 1
      black_square_row = line_list[1] - 1
      adj_value = line_list[2]

      self.board[black_square_row][black_square_col] = BlackSquare(adj_value)
      self.num_empty_white_squares -= 1
    

    # Generate a coordinate versions of the board
    self.coord_board = []

    for x in range(self.num_rows):
      coord_list = []
      for y in range(self.num_cols):
        coord_list.append(Coordinate(x, y))
      self.coord_board.append(coord_list)
    
    self.transpose_coord_board = [list(l) for l in zip(*self.coord_board)]

    # Open the config file for reading
    with open('config.json', 'r') as config_file:
      self.config_settings = json.loads(config_file.read().replace('\n', ''))

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
      self.num_empty_white_squares -= 1
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

    def check_update_square_shine(board, coord, num_empty_white_squares):
      """Determines if a square can be safely shined on.

      Returns a ShineInfo flag. 
      """
      square = board[coord.x][coord.y]

      if square.color == Color.WHITE:
        if square.has_bulb:
          return ShineInfo.FOUND_BULB
        else:
          if not square.has_shine:
            num_empty_white_squares[0] -= 1
            square.has_shine = True

          return ShineInfo.NO_ERROR
      
      return ShineInfo.FOUND_BLACK_SQUARE
    
    # Temporary variables so changes are not permanent until safe shining is ensured
    tmp_board = self.board
    tmp_num_empty_white_squares = [self.num_empty_white_squares]

    # Create a list of adjacency lists - used for determining where the bulb shines
    adj_coord_lists = []

    adj_coord_lists.append(self.coord_board[coord.x][:coord.y][::-1])           # Row from this column to the left
    adj_coord_lists.append(self.coord_board[coord.x][coord.y + 1:])             # Row from this column to the right
    adj_coord_lists.append(self.transpose_coord_board[coord.y][:coord.x][::-1]) # Column from this row up
    adj_coord_lists.append(self.transpose_coord_board[coord.y][coord.x + 1:])   # Column from this row down

    for coord_list in adj_coord_lists:
      for coord in coord_list:
        result = check_update_square_shine(tmp_board, coord, tmp_num_empty_white_squares)
    
        if result == ShineInfo.FOUND_BULB:
          return False
        elif result == ShineInfo.FOUND_BLACK_SQUARE:
          break

    # Copy changes to the real board
    self.board = tmp_board
    self.num_empty_white_squares = tmp_num_empty_white_squares[0]

    return True

  def is_solved(self):
    """Checks to see if a board is solved.

    Returns True if the board is solved, False otherwise.
    """

    def check_adj_bulbs(coord):
      """Checks to see if a square has the required number of adjacent bulbs."""
      square = self.board[coord.x][coord.y]

      if square.color == Color.WHITE or square.adj_value == BlackSquareAdjValue.DONT_CARE_ADJ:
        return True
      
      # Adjacent bulb processing
      adj_coords = []

      if not coord.x == 0:
        adj_coords.append(Coordinate(coord.x - 1, coord.y))

      if not coord.x == self.num_rows - 1:
        adj_coords.append(Coordinate(coord.x + 1, coord.y))
      
      if not coord.y == 0:
        adj_coords.append(Coordinate(coord.x, coord.y - 1))
      
      if not coord.y == self.num_cols - 1:
        adj_coords.append(Coordinate(coord.x, coord.y + 1))
      
      target_bulbs = square.adj_value

      for adj_coord in adj_coords:
        adj_square = self.board[adj_coord.x][adj_coord.y]

        if adj_square.color == Color.WHITE and adj_square.has_bulb:
          target_bulbs -= 1

      return target_bulbs == 0

    if self.num_empty_white_squares != 0:
      return False

    if self.config_settings["enforce_adj_quotas"] == 'True':
      for coord_row in self.coord_board:
        for coord in coord_row:
          if not check_adj_bulbs(coord):
            return False
    
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

print(b.is_solved())