import sys
import board as board_class


if __name__ == '__main__':

  if len(sys.argv) == 1:
    # No argument for configuration file, use default
    board_config_file = 'default.cfg'
  
  else:
    # We have an external configuration file (the second item in sys.argv)
    board_config_file = sys.argv[1]


  b = board_class.Board(board_config_file) 

  b.visualize()
  for i in range(100):
    b.place_bulb_randomly()
  b.visualize()
  print(b.check_solved())