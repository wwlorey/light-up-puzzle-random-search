import sys
import json
import board as board_class


if __name__ == '__main__':

  if len(sys.argv) == 1:
    # No argument for configuration file, use default
    config_file = 'default.cfg'
  
  else:
    # We have an external configuration file (the second item in sys.argv)
    config_file = sys.argv[1]


with open(config_file, 'r') as c:
  config = json.loads(c.read().replace('\n', ''))

log = open(config["log_file_path"], 'w')
print("Result Log\n\n")

b = board_class.Board(config_file) 

max_fitness = 0

for run_count in range(1, config["num_experiment_runs"] + 1):

  eval_count = 1

  while eval_count <= config["num_fitness_evaluations"]:
    if not b.place_bulb_randomly():
      b.clear_board()

    if b.check_valid_solution():
      if b.get_fitness() > max_fitness:
        max_fitness = b.get_fitness()
        log.write("Run %i\n" % run_count)
        log.write("%i\t%i\n" % (eval_count, max_fitness))
        print("Run %i\n" % run_count)
        print("%i\t%i\n" % (eval_count, max_fitness))

      eval_count += 1
    
    print(str(eval_count))



