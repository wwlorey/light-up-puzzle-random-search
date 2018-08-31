import matplotlib.pyplot as plt
import numpy as np

# The run data for each experiment's fittest solution was scraped from the log files and put in the following files for easy access
soln_data_files = ['random_gen_soln_data.txt', 'website_puzzle_soln_data.txt']

# Formatting parameters
soln_data_titles = ['Randomly Generated Puzzles', 'Provided Puzzle']
soln_scales = [250, 300]

for index, file_name in enumerate(soln_data_files):
    with open(file_name, 'r') as file:
        eval_list = []
        fitness_list = []
        
        # Read the input file into the above lists
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
    
    # Graph evaluations vs. fitness
    plt.plot(eval_list, fitness_list, '-ro', linewidth = 2.0)

    # Set axis display parameters
    plt.xticks(np.arange(0, max(eval_list) + 500, soln_scales[index]))
    plt.yticks(np.arange(0, max(fitness_list) + 10, 10))
    plt.xlim(0, eval_list[-1] + (len(eval_list) * 20))

    # Include necessary labels
    plt.xlabel('evaluations')
    plt.ylabel('fitness')
    plt.title('Evaluations vs. Fitness for ' + soln_data_titles[index] + '\n(without enforcing black cell number constraint)')
    plt.annotate('Maximum fitness: ' + str(fitness_list[-1]) + '\nEvaluation number: ' + str(eval_list[-1]), xy = (eval_list[-1], fitness_list[-1]),
        xytext=(1, -60), ha='right', textcoords='offset points', arrowprops=dict(arrowstyle = 'simple', shrinkA = 0))

    # Save and close the plot
    plt.savefig(file_name[:file_name.find('data')] + 'graph.png')
    plt.close()
