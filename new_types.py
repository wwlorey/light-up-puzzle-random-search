import json


class Coordinate:
  def __init__(self, x, y):
    self.x = x
    self.y = y
  
  def __str__(self):
    """Returns an ordered pair in string form."""
    return '(' + str(self.x) + ', ' + str(self.y) + ')'


class Board:
  def __init__(self):
    self.black_squares = {}
    self.bulbs = set([])

    # Load configuration settings
    with open('config.json', 'r') as config_file:
      self.config_settings = json.loads(config_file.read().replace('\n', ''))

    if self.config_settings["generate_board"] == "True":
      # Generate random initial board state
      pass

    else:
      # Read initial board state
      with open(self.config_settings["input_file_name"], 'r') as input_file:
        # Read line 0 (number of columns)
        self.num_cols = int(input_file.readline())

        # Read line 1 (number of rows)
        self.num_rows = int(input_file.readline())

        # Read line 2 to EoF (coordinates of black squares and their adjacency values)
        for row in input_file:
          black_square_data = [int(i) for i in row.split()]
          self.black_squares[Coordinate(black_square_data[0] - 1, black_square_data[1] - 1)] = black_square_data[2]

  def put_bulb(self, coord):
    """Attempts to place a bulb at coord position on the board.

    Returns True on success, False on fail.
    """

    def has_delimiting_black_square(coord_a, coord_b):
      """Checks for a black square between the given coordinates' shared row or column.

      Returns True if there is a delimiting black square, False otherwise.
      """
      # test_cases_list = [
      #   {
      #     "upper_bound":   max(coord_a.y, coord_b.y),
      #     "lower_bound":   max(coord_a.y, coord_b.y),
      #     "row_or_col":    coord_a.x,
      #     "test_case_row": True
      #   },
      #   {
      #     "upper_bound":   max(coord_a.x, coord_b.x),
      #     "lower_bound":   max(coord_a.x, coord_b.x),
      #     "row_or_col":    coord_a.y,
      #     "test_case_row": False
      #   }
      # ]

      # for test_case in test_cases_list:
      #   for black_square in self.black_squares:
      #     black_square_check_coord_row_or_col = black_square.x if test_case["test_case_row"] else black_square.y
      #     black_square_check_coord_bound      = black_square.y if test_case["test_case_row"] else black_square.x

      #     if  black_square_check_coord_row_or_col == test_case["row_or_col"]   \
      #         and (test_case["upper_bound"] > black_square_check_coord_bound   \
      #         and test_case["lower_bound"] < black_square_check_coord_bound):
      #       return True
          
      # return False # No black square delimeter was found

      if coord_a.x == coord_b.x:
        # Check for delimiting black square in row
        upper_bound = max(coord_a.y, coord_b.y)
        lower_bound = min(coord_a.y, coord_b.y)
        row = coord_a.x

        for black_square in self.black_squares:
          if black_square.x == row and (upper_bound > black_square.y and lower_bound < black_square.y):
              return True
        
        return False # No black square delimiter was found
      
      if coord_a.y == coord_b.y:
        # Check for delimiting black square in column
        upper_bound = max(coord_a.x, coord_b.x)
        lower_bound = min(coord_a.x, coord_b.x)
        col = coord_a.y

        for black_square in self.black_squares:
          if black_square.y == col and (upper_bound > black_square.x and lower_bound < black_square.x):
              return True
        
        return False # No black square delimiter was found

      # There is no shared row or column, or the coordinates are the same. Delimiting square is irrelevant
      return True

    # Check for duplicate bulbs in rows & columns
    for bulb_coord in self.bulbs:
      if (coord.x == bulb_coord.x or coord.y == bulb_coord.y) and not has_delimiting_black_square(coord, bulb_coord):
        return False # We cannot safely place a bulb at coord

    self.bulbs.add(coord)
    return True

  def visualize(self):
    """Prints a string representation of the board.

    '_' Empty white square
    'x' Black square (with 0 <= x <= 5)
    '!' Light bulb
    """
    board = [ [ '_' for row in range(self.num_rows) ] for col in range(self.num_cols) ]

    for coord, value in self.black_squares.items():
      board[coord.x][coord.y] = str(value)
    
    for coord in self.bulbs:
      board[coord.x][coord.y] = '!'
    
    for row in board:
      for item in row:
        print(item + ' ', end='')

      print()

    print()
  
  def check_solved(self):



b = Board()

for x in range(b.num_rows):
  for y in range(b.num_cols):
    c = Coordinate(x, y)
    b.put_bulb(c)
    b.visualize()
    