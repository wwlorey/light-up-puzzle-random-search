import json
import time
import random


ADJ_VALUE_DONT_CARE = 5
MAX_NUM_RANDOM_PLACEMENTS = 100


class Coordinate:
  def __init__(self, x, y):
    self.x = x
    self.y = y
  
  def __str__(self):
    """Returns an ordered pair in string form."""
    return '(' + str(self.x) + ', ' + str(self.y) + ')'
  
  def __eq__(self, other):
    return self.x == other.x and self.y == other.y

  def __hash__(self):
    return (self.x + 1) * 100000 + self.y


class Board:
  def __init__(self):
    self.black_squares = {}
    self.bulbs = set([])

    # Load configuration settings
    with open('config.json', 'r') as config_file:
      self.config_settings = json.loads(config_file.read().replace('\n', ''))

    if self.config_settings["generate_board"]:
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
      
    # Generate coordinate versions of the board
    self.coord_board = []

    for x in range(self.num_rows):
      coord_list = []
      for y in range(self.num_cols):
        coord_list.append(Coordinate(x, y))
      self.coord_board.append(coord_list)
    
    self.transpose_coord_board = [list(l) for l in zip(*self.coord_board)]

    # Seed the random number generator
    if self.config_settings["use_external_seed"]:
      # Use external seed
      random.seed(self.config_settings["seed"])
    else:
      # Default to system time as seed
      random.seed(time.time)

    self.num_empty_squares = -1 # This value is updated during solution verification

  def put_bulb(self, coord):
    """Attempts to place a bulb at coord position on the board.

    Returns True on success, False on fail.
    """

    def has_delimiting_black_square(coord_a, coord_b):
      """Checks for a black square between the given coordinates' shared row or column.

      Returns True if there is a delimiting black square, False otherwise.
      """
      if coord_a == coord_b:
        return True # Delimiting square is irrelevant

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

    if coord in self.black_squares:
      return False # Can't place a bulb on a black square 

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
    """Checks to see if the board is solved.

    Returns True if the following conditions are met:
      1. Every non-black square is shined on by a bulb.
      2. No bulbs shine on eachother.
      3. Every black square has the required adjacent bulbs. (can be disabled using config file setting)
    """

    def get_adj_bulbs(coord):
      """Returns the number of adjacent bulbs to coordinate coord"""
      adj_coords = []
      num_adj_bulbs = 0

      if not coord.x == 0:
        adj_coords.append(Coordinate(coord.x - 1, coord.y))

      if not coord.x == self.num_rows - 1:
        adj_coords.append(Coordinate(coord.x + 1, coord.y))
      
      if not coord.y == 0:
        adj_coords.append(Coordinate(coord.x, coord.y - 1))
      
      if not coord.y == self.num_cols - 1:
        adj_coords.append(Coordinate(coord.x, coord.y + 1))
      
      for coord in adj_coords:
        if coord in self.bulbs:
          num_adj_bulbs += 1
      
      return num_adj_bulbs


    # Create and populate set of shined squares
    shined_squares = set([])

    for bulb_coord in self.bulbs:
      # Create a list of adjacency lists - used for determining where the bulb shines
      adj_coord_lists = []

      adj_coord_lists.append(self.coord_board[bulb_coord.x][:bulb_coord.y][::-1])           # Row from this column to the left
      adj_coord_lists.append(self.coord_board[bulb_coord.x][bulb_coord.y + 1:])             # Row from this column to the right
      adj_coord_lists.append(self.transpose_coord_board[bulb_coord.y][:bulb_coord.x][::-1]) # Column from this row up
      adj_coord_lists.append(self.transpose_coord_board[bulb_coord.y][bulb_coord.x + 1:])   # Column from this row down

      for coord_list in adj_coord_lists:
        for coord in coord_list:
          if coord in self.black_squares:
            break # Shine cannot propagate any further
          elif coord in self.bulbs:
            return False # Redundant check for bulb on bulb shining
          else:
            shined_squares.add(coord)
    
    # Verify all squares are accounted for
    if (len(self.black_squares) + len(self.bulbs) + len(shined_squares)) != (self.num_cols * self.num_rows):
      self.num_empty_squares = (self.num_cols * self.num_rows) - (len(shined_squares) + len(self.black_squares) + len(self.bulbs))
      return False

    self.num_empty_squares = 0

    # Check black square conditions
    if self.config_settings["enforce_adj_quotas"]:
      for coord, adj_value in self.black_squares.items():
        if adj_value < ADJ_VALUE_DONT_CARE and get_adj_bulbs(coord) != adj_value:
          return False

    return True

  def place_bulb_randomly(self):
    """Attempts to put a bulb randomly on the board in a valid location.

    Stops trying to put a bulb after MAX_NUM_RANDOM_PLACEMENTS tries.
    Returns True if successful, False otherwise.
    """

    def get_rand_coord():
      """Returns a random coordinate ranging in the space (num_cols, num_rows)"""
      return Coordinate(random.randint(0, self.num_cols - 1), random.randint(0, self.num_cols - 1))


    coord = get_rand_coord()
    count = 0

    while count < MAX_NUM_RANDOM_PLACEMENTS and not self.put_bulb(coord):
      coord = get_rand_coord()
      count += 1
    
    if count < MAX_NUM_RANDOM_PLACEMENTS:
      return True
    
    return False
