import matplotlib.pyplot as plt
import numpy as np

# Run data for each experiment's most fit solution was scraped from the log files and put in the following files
soln_data_files = ['random_gen_soln_data.txt', 'website_puzzle_soln_data.txt']

soln_data_titles = ['Randomly Generated Puzzles', 'Provided Puzzle']


for index, file_name in enumerate(soln_data_files):
    with open(file_name, 'r') as file:
        eval_list = []
        fitness_list = []
        
        line_count = -1

        for line in file:
            line_count += 1

            if line_count == 1:
                split_line = [int(_) for _ in line.split('\t')]

                eval_list.append(split_line[0])
                fitness_list.append(split_line[1])

            elif line_count == 2:
                # Reset the line count
                line_count = -1
    
    
    plt.plot(eval_list, fitness_list)
    plt.xlabel('evaluations')
    plt.ylabel('fitness')
    plt.xlim([eval_list[0], eval_list[-1]])
    plt.ylim([fitness_list[0], fitness_list[-1]])
    x = eval_list
    plt.xticks(np.arange(min(x), max(x), 70))
    plt.title('Evaluations vs. Fitness for ' + soln_data_titles[index])
    plt.show()