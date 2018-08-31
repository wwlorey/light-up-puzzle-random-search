import json
import time
import random
import coordinate as coord_class


class Board:
  def __init__(self, board_config_file):
    """Initializes the board class."""

    def generate_coord_boards():
      """Generates a 2D coordinate board and its transpose.
      
      These are used when verifying solutions and creating random boards.
      """
      self.coord_board = []

      for x in range(self.num_rows):
        coord_list = []
        for y in range(self.num_cols):
          coord_list.append(coord_class.Coordinate(x, y))

        self.coord_board.append(coord_list)
      
      self.transpose_coord_board = [list(l) for l in zip(*self.coord_board)]


    def generate_random_board():
      """Randomly generates a solvable board.

      Solvable boards are generated by iteratively placing black squares (with probability
      dictated by the configuration file) and required bulbs around each square before
      removing the bulbs, leaving a board with at least one solution.

      This function should only be called in __init__
      """

      def get_max_black_square_value(adj_coord_list):
        """Returns the maximum allowable of black squares for a coordinate.

        This is calculated using the list of coordinates adjacent to the coordinate in question.
        """
        if len(adj_coord_list) == 2:
          # Square is in a corner
          return 2
        
        if len(adj_coord_list) == 3:
          # Square is on a straightaway 
          return 3
        
        if len(adj_coord_list) == 4: 
          # Square is in the middle somewhere
          return 4
        
        # Undefined behavior
        return 0


      self.black_squares = {}
      self.bulbs = set([])

      if self.config_settings["override_random_board_dimensions"]:
        self.num_rows = self.config_settings["override_num_rows"]
        self.num_cols = self.config_settings["override_num_cols"]

      else:
        min_dimension = self.config_settings["min_random_board_dimension"]
        max_dimension = self.config_settings["max_random_board_dimension"]

        self.num_rows = random.randint(min_dimension, max_dimension)
        self.num_cols = random.randint(min_dimension, max_dimension)

      generate_coord_boards()

      # Create a list of shuffled coordinates used in assigning black squares
      shuffled_coords = []
      for row in self.coord_board:
        for coord in row:
          shuffled_coords.append(coord)

      random.shuffle(shuffled_coords)

      # Assign black squares to the board
      for coord in shuffled_coords:
        if not coord in self.bulbs and random.random() <= self.config_settings["black_square_placement_prob"]:
          adj_coord_list = self.get_adj_coords(coord)
          num_placed_bulbs = 0

          # Compute the random max value for this black square
          max_value = random.choices(list(range(0, self.config_settings["adj_value_dont_care"])), self.config_settings["black_square_value_probabilities"])[0]

          # Put a placeholder black square to ensure the maximum amount of bulbs can be placed
          self.black_squares[coord] = 5

          # Place bulbs around the square, if allowed
          for adj_coord in adj_coord_list:
            if num_placed_bulbs < max_value and self.place_bulb(adj_coord):
              num_placed_bulbs += 1

          # Update the real black square value to match the number of adjacent bulbs
          self.black_squares[coord] = num_placed_bulbs
        
      if not self.check_completely_solved():
        # Fill non-lit coordinates with black squares of value 5
        for coord in shuffled_coords:
          if not coord in self.shined_squares and not coord in self.bulbs and not coord in self.black_squares:
            self.black_squares[coord] = 5
      

    self.black_squares = {}
    self.bulbs = set([])
    self.log_str = 'Result Log\n'

    # Load configuration settings
    with open(board_config_file, 'r') as config_file:
      self.config_settings = json.loads(config_file.read().replace('\n', ''))

    # Seed the random number generator
    self.log_str += 'seed: '
    if self.config_settings["use_external_seed"]:
      # Use external seed
      seed_val = self.config_settings["seed"]

    else:
      # Default to system time as seed
      seed_val = time.time()
    
    print(seed_val)

    random.seed(seed_val)
    self.log_str += str(seed_val) + '\n'

    if self.config_settings["generate_board"]:
      # Generate random initial board state
      generate_random_board()

      while len(self.black_squares) == (self.num_cols * self.num_rows) or not self.check_completely_solved():
        generate_random_board()
      
      # Re-initialize the bulb set
      self.bulbs = set([])

      self.log_str += 'randomly generated puzzle.\n' + \
                      '\tmax_num_random_board_gen_placements: ' + str(self.config_settings["max_num_random_board_gen_placements"]) + '\n' + \
                      '\tmin_random_board_dimension: ' + str(self.config_settings["min_random_board_dimension"]) + '\n' + \
                      '\tmax_random_board_dimension: ' + str(self.config_settings["max_random_board_dimension"]) + '\n' + \
                      '\toverride_random_board_dimensions: ' + str(self.config_settings["override_random_board_dimensions"]) + '\n' + \
                      '\toverride_num_rows: ' + str(self.config_settings["override_num_rows"]) + '\n' + \
                      '\toverride_num_cols: ' + str(self.config_settings["override_num_cols"]) + '\n'

    else:
      # Read initial board state
      with open(self.config_settings["input_file_path"], 'r') as input_file:
        self.log_str += 'puzzle source: ' + self.config_settings["input_file_path"] + '\n'

        # Read line 0 (number of columns)
        self.num_cols = int(input_file.readline())

        # Read line 1 (number of rows)
        self.num_rows = int(input_file.readline())

        # Read line 2 to eof (coordinates of black squares and their adjacency values)
        for row in input_file:
          black_square_data = [int(i) for i in row.split()]
          self.black_squares[coord_class.Coordinate(black_square_data[1] - 1, black_square_data[0] - 1)] = black_square_data[2]
        
      # Generate coordinate versions of the board
      generate_coord_boards()
      
    self.log_str += 'board size (#rows x #cols): ' + str(self.num_rows) + ' x ' + str(self.num_cols) + '\n'

    self.num_empty_squares = -1 # This value is updated during solution verification


  def get_random_coord(self):
    """Returns a random coordinate ranging in the space (num_cols, num_rows)."""
    return coord_class.Coordinate(random.randint(0, self.num_rows - 1), random.randint(0, self.num_cols - 1))
  

  def get_adj_coords(self, coord):
    """Returns a list of coordinates adjacent to coordinate coord"""
    adj_coords = []

    if not coord.x == 0:
      adj_coords.append(coord_class.Coordinate(coord.x - 1, coord.y))

    if not coord.x == self.num_rows - 1:
      adj_coords.append(coord_class.Coordinate(coord.x + 1, coord.y))
    
    if not coord.y == 0:
      adj_coords.append(coord_class.Coordinate(coord.x, coord.y - 1))
    
    if not coord.y == self.num_cols - 1:
      adj_coords.append(coord_class.Coordinate(coord.x, coord.y + 1))
    
    return adj_coords


  def place_bulb(self, coord):
    """Attempts to place a bulb at coord position on the board.

    Returns True on success, False on fail.
    """
    if coord in self.black_squares:
      return False # Can't place a bulb on a black square 

    # Check for cross-shine in the coordinate's row (same x value)
    matching_x_coord_bulbs = [c for c in self.bulbs if c.x == coord.x]
    found_x_delimeter = False if len(matching_x_coord_bulbs) else True

    for bulb_coord in matching_x_coord_bulbs:
      if bulb_coord.x == coord.x:
        min_y = min(bulb_coord.y, coord.y)
        max_y = max(bulb_coord.y, coord.y)

        if max_y - min_y < 2:
          return False
        
        for black_coord in [c for c in self.black_squares if c.x == coord.x]:
          if black_coord.y < max_y and black_coord.y > min_y:
            found_x_delimeter = True
            break

    if not found_x_delimeter:
      return False
      
    # Check for cross-shine in the coordinate's column (same y value)
    matching_y_coord_bulbs = [c for c in self.bulbs if c.y == coord.y]
    found_y_delimeter = False if len(matching_y_coord_bulbs) else True

    for bulb_coord in matching_y_coord_bulbs:
      if bulb_coord.y == coord.y:
        min_x = min(bulb_coord.x, coord.x)
        max_x = max(bulb_coord.x, coord.x)

        if max_x - min_x < 2:
          return False
        
        for black_coord in [c for c in self.black_squares if c.y == coord.y]:
          if black_coord.x < max_x and black_coord.x > min_x:
            found_y_delimeter = True
            break
    
    if not found_y_delimeter:
      return False

    self.bulbs.add(coord)
    return True
    

  def visualize(self):
    """Prints a string representation of the board.

    '_' Empty white square
    'x' Black square (with 0 <= x <= 5)
    '!' Light bulb
    """
    board = [ [ '_' for col in range(self.num_cols) ] for row in range(self.num_rows) ]

    for coord, value in self.black_squares.items():
      board[coord.x][coord.y] = str(value)
    
    for coord in self.bulbs:
      board[coord.x][coord.y] = '!'
    
    for row in board:
      for item in row:
        print(item + ' ', end='')

      print()

    print()

  
  def get_num_bulbs(self, coord_list):
    """Returns the number of bulbs in coord_list"""
    num_adj_bulbs = 0

    for coord in coord_list:
      if coord in self.bulbs:
        num_adj_bulbs += 1
    
    return num_adj_bulbs
   

  def get_num_black_squares(self, coord_list):
    """Returns the number of black squares in coord_list"""
    num_adj_black_squares = 0  

    for coord in coord_list:
      if coord in self.black_squares:
        num_adj_black_squares += 1
    
    return num_adj_black_squares 
    

  def check_completely_solved(self):
    """Checks to see if the board is *completely* solved.

    Returns True if the following conditions are met:
      1. Every non-black square is shined on by a bulb.
      2. No bulbs shine on eachother. (guaranteed by place_bulb() function)
      3. Every black square has the required adjacent bulbs. (can be disabled using config file setting)
    """
    # Create and populate set of shined squares
    self.shined_squares = set([])

    if len(self.bulbs) == 0:
      return False

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
            self.shined_squares.add(coord)

    # Verify all squares are accounted for
    if (len(self.black_squares) + len(self.bulbs) + len(self.shined_squares)) != (self.num_cols * self.num_rows):
      self.num_empty_squares = (self.num_cols * self.num_rows) - (len(self.shined_squares) + len(self.black_squares) + len(self.bulbs))
      return False

    self.num_empty_squares = 0

    return self.check_valid_solution()

    return True


  def check_valid_solution(self):
    """Checks to see if the board is *valid*.

    Returns True if the following conditions are met:
      1. No bulbs shine on eachother. (guaranteed by place_bulb() function)
      2. Every black square has the required adjacent bulbs. (can be disabled using config file setting)
    """
    # Check black square conditions
    if self.config_settings["enforce_adj_quotas"]:
      for coord, adj_value in self.black_squares.items():
        if adj_value < self.config_settings["adj_value_dont_care"] and self.get_num_bulbs(self.get_adj_coords(coord)) != adj_value:
          return False
    
    return True
    

  def place_bulb_randomly(self):
    """Attempts to put a bulb randomly on the board in a valid location.

    Stops trying to put a bulb after max_num_random_bulb_placements tries.
    Returns True if successful, False otherwise.
    """
    coord = self.get_random_coord()
    count = 0

    while count < self.config_settings["max_num_random_bulb_placements"] and not self.place_bulb(coord):
      coord = self.get_random_coord()
      count += 1
    
    if count < self.config_settings["max_num_random_bulb_placements"]:
      return True
    
    return False
  
  
  def write_to_soln_file(self, num_lit):
    """Writes problem information to the solution file specified in the configuration file."""
    with open(self.config_settings["soln_file_path"], 'w') as soln_file:
      soln_file.write(str(self.num_cols) + '\n')
      soln_file.write(str(self.num_rows) + '\n')

      for coord in self.black_squares:
        soln_file.write(str(coord.y) + ' ' + str(coord.x) + ' ' + str(self.black_squares[coord]) + '\n')
      
      soln_file.write(str(num_lit) + '\n')

      for coord in self.bulbs:
        soln_file.write(str(coord.y) + ' ' + str(coord.x) + '\n')
      
      soln_file.write('\n')


  def get_fitness(self):
    """Returns the fitness of the puzzle.

    Fitness is defined as the number of lit squares on the board.
    """
    return len(self.shined_squares)
  

  def clear_board(self):
    """Clears all bulbs from the board."""
    self.bulbs = set([])