# Assuming the files contain numerical values on the first line which can be averaged
# algos = ['ABR', 'GRBR', 'WDC', 'Spotify', 'Cars', 'Movies]
algos = ['Movies']
lvs = [ '9', '10', '11']
weights = ['weighted', 'unweighted']
for algo in algos:
    for lv in lvs:
        for weight in weights:
            file_paths = [
                '/xxxx/xxxx/Join-Game/Join_Summary/{}/sum_similarity_lv{}_{}1_{}.dat'.format(weight, lv, algo, weight),
                '/xxxx/xxxx/Join-Game/Join_Summary/{}/sum_similarity_lv{}_{}2_{}.dat'.format(weight, lv, algo, weight),
                '/xxxx/xxxx/Join-Game/Join_Summary/{}/sum_similarity_lv{}_{}3_{}.dat'.format(weight, lv, algo, weight)
            ]

            # Define the output file path
            output_file_path = '/xxxx/xxxx/Join-Game/Results/sum_similarity_lv{}_{}_avg_{}.dat'.format(lv, algo, weight)

            # Open the three input files and the output file
            with open(file_paths[0], 'r') as file1, open(file_paths[1], 'r') as file2, open(file_paths[2], 'r') as file3, open(output_file_path, 'w+') as output_file:
                # Read and process each line from the files simultaneously
                for line1, line2, line3 in zip(file1, file2, file3):
                    # Split each line on the tab to separate the identifier and the value
                    id1, value1 = line1.split('\t')
                    id2, value2 = line2.split('\t')
                    id3, value3 = line3.split('\t')

                    # Convert the values to float
                    value1 = float(value1)
                    value2 = float(value2)
                    value3 = float(value3)

                    # Calculate the average of the values
                    avg_value = (value1 + value2 + value3) / 3

                    # Write the average value to the output file, using the identifier from the first file
                    output_file.write("{}\t{:.10f}\n".format(id1, avg_value))
print("Done")
