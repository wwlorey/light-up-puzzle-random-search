import sys
import light_up_puzzle as puzzle_class
import light_up_puzzle_config as config_class


if __name__ == '__main__':

  if len(sys.argv) == 1:
    # No config file provided, use default
    config_file = 'default.cfg'
  
  else:
    # Use the provided config file
    config_file = sys.argv[1]

  config = config_class.LightUpPuzzleConfig(config_file)

  log = open(config.settings["log_file_path"], 'w')
  log.write("Result Log\n\n")

  for run_count in range(1, config.settings["num_experiment_runs"] + 1):
    puzzle = puzzle_class.LightUpPuzzle(config) 
    max_fitness = 0
    eval_count = 1

    while eval_count <= config.settings["num_fitness_evaluations"]:
      print("Eval count: " + str(eval_count))

      if not puzzle.place_bulb_randomly():
        puzzle.clear_board()

      if puzzle.check_valid_solution():
        if puzzle.get_fitness() > max_fitness:
          max_fitness = puzzle.get_fitness()
          log.write("Run %i\n" % run_count)
          log.write("%i\t%i\n\n" % (eval_count, max_fitness))

          puzzle.write_to_soln_file()

        eval_count += 1
