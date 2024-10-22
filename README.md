This repository contains all the information that is necessary to conduct the join game experiment.

This module includes scripts to generate TPC-H benchmark data and create the appropriate PostgreSQL tables. The relavant files are located at ./TPC-H_DataGen.

## Changes to PostgreSQL Environment

To be able to run the algorithms that we have conducted experiment with, just follow the steps below:
1. Install the PostgreSQL on your system.
2. Once the PostgreSQL system is installed, go to 'src/backend/executor/nodeNestloop.c' and 'src/include/nodes/execnodes.h' paths to change the contents of those files with the those of the algorithms provided. You can find the code related to the algorithms in the 'Algorithms' folder and each algorithm has it's own subfolder with their own files.
Note: If you want to perform the experiment with the SMS algorithm, in addition to the above 2 files, you also need to make changes to 'src/backend/executor/nodeMergejoin.c' and 'src/backend/executor/nodeSort.c' files with the contents of those same named files from the SMS folder.

## Uploading the datasets

Once the code changes are made, you can go ahead and upload the datasets for your experiments. You can generate the TPC-H benchamrk data for all the TPC-H relted experiments. As for the Movies, Cars and WDC datasets, you can find the links related to those in the paper and can download the datasets from those links and upload them to the PostgreSQL environment.

Once the datasets have been loaded to the PostgreSQL environment, you can create your own shuffles for them using the scripts, 'dataset_shuffler_Cars.py', 'dataset_shuffler_Movies.py', 'dataset_shuffler_WDC.py' and 'script_full_load_custom.py'. These scripts will create 3 different shuffles for each dataset, so that there won't be any bias in the results.

## Running the experiments

Once the necessary changes have been made to the code base and the datasets have been uploaded into the PostgreSQL, you can run the experiments by running any of the scripts in the Queries folder. For the TCH-H related queries, you need to go into the 'TPCH_Queries' subfolder and run the 'script_experiment.py' script and for the other dataset related experiments, you can run the 'similarity_Cars.py', 'similarity_Movies.py' or 'similarity_WDC.py' scripts.