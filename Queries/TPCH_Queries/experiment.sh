#!/bin/bash

# For non-stopping tests, you may use the command below,
# nohup bash -c './experiment.sh' &

# Define the path variables
path_1="test"
path_2="OSL(L100_N500_M5000)"

# Define the query and index arrays
queries=("Q9" "Q10" "Q11" "Q15" "Q8" "Q9_3R")
indexes=("0" "1" "1_5")

# Loop through each query
for query in "${queries[@]}"; do
    # Determine the relation based on the query
    if [[ "$query" == "Q8" || "$query" == "Q9_3R" || "$query" == "Q2" || "$query" == "Q3" || "$query" == "Q5" ]]; then
        relation="3R"
    else
        relation="2R"
    fi

    # Use "Q9" for query_path if the query is "Q9_3R"
    if [[ "$query" == "Q9_3R" ]]; then
        query_path="Q9"
    else
        query_path="$query"
    fi
    
    # Loop through each index
    for index in "${indexes[@]}"; do

        # Use "15" for query_path if the query is "1_5"
        if [[ "$index" == "1_5" ]]; then
            z_val="15"
        else
            z_val="$index"
        fi

        # Construct the directory path and full path
        dir_path="./Results/${path_1}/${path_2}/${relation}/${query_path}"
        full_path="${dir_path}/${z_val}"

        # Create the directory if it does not exist
        mkdir -p "$dir_path"

        # Execute the python script with constructed variables
        python path/to/script_experiment.py "$full_path" "$index" "$query"
    done
done


