#!/bin/python
import sys
import datetime
import psycopg2
from time import time

# Replace these variables with your own psql connection details
DATABASE = 'leeyongh'
USER = 'leeyongh'
HOST = '/tmp/'
PORT = '5245'

# Verify that exactly two additional command line arguments are provided
if len(sys.argv) != 4:
    print("Usage: script_name <verbose_output_file_path> <testing_z_value> <query>")
    print("Error: Exactly two arguments are required: the path for the verbose output file and the testing z value.")
    sys.exit(1) # Exit with a non-zero value to indicate an error

# Parameters setting
SIGMA = .99
TIME_LIMIT = 180                # 30 mins = 1800, 15 mins = 900, 3 mins = 180
DATA_LIMIT = 100                # Limit the number of data points
MAX_GLOBAL_RETRIES = 3          # Maximum number of retries if results differ significantly
STEP_SIZE = 1.5                 # Data point step size (Exponent part should be greater than 1)
TEST_NUMBER = 1                 # The number of tests for each query
ITER_SIZE = 100                 # The number of rows per a round trip (Default = 2000)
Z_VALAUE = str(sys.argv[2])     # z-values = {0, 1, 1_5}

# Data points to store the information
data_points = []
for i in range(100):
    value = ITER_SIZE * (STEP_SIZE ** i)
    data_points.append(int(value))

# Files
file = str(sys.argv[1])                     # file path,    e.g) file = 'result'
result_log = file + '.log'                  # str(sys.argv[1]) + '.log'
result_summary = file + '.txt'              # str(sys.argv[1]) + '.txt'
result_data_unweight = file + '.dat'        # str(sys.argv[1]) + '.dat'
result_data_weight = file + '_weight.dat'   # str(sys.argv[1]) + '.dat'

# Test enviroment setting
settings = [
    'set enable_material = OFF;',
    'set max_parallel_workers_per_gather = 0;',
    'set enable_seqscan = ON;',
    'set enable_indexonlyscan = OFF;',
    'set enable_indexscan = OFF;',
    'set enable_bitmapscan = OFF;',
    'set enable_block = OFF;',
    'set enable_fastjoin = OFF;',
    'set enable_fliporder = OFF;',
    
    'set enable_nestloop = ON;',
    'set enable_hashjoin = OFF;',
    'set enable_mergejoin = OFF;',
    
    'set work_mem = "64MB";',                  # Try to see difference varying work_mem
    'set statement_timeout = 1800000;',        # 30 mins = 1800000
    ]


# Construct queries
def construct_join_queries(val):
    queries = []
    sch_vals = ['1', '2', '3']
    for sch_val in sch_vals:
        if str(sys.argv[3]) == 'Q9':
            # Q9 - TPCH
            queries.append("select * from partsupp1%s%s, lineitem1%s%s where ps_partkey = l_partkey LIMIT 120000;" % (sch_val, val, sch_val, val))
        elif str(sys.argv[3]) == 'Q10':
            # Q10 - TPCH
            queries.append("select * from customer1%s%s, order1%s%s where c_custkey = o_custkey LIMIT 8000;" % (sch_val, val, sch_val, val))
        elif str(sys.argv[3]) == 'Q11':           
            # Q11(Modified) - TPCH
            queries.append("select * from order1%s%s, lineitem1%s%s where o_orderdate = l_shipdate LIMIT 150000;" % (sch_val, val, sch_val, val))
        elif str(sys.argv[3]) == 'Q12':
            # Q12 - TPCH
            queries.append("select * from order1%s%s, lineitem1%s%s where o_orderkey = l_orderkey LIMIT 30000;" % (sch_val, val, sch_val, val))
        elif str(sys.argv[3]) == 'Q15':
            # Q15 - TPCH
            queries.append("select * from supplier1%s%s, lineitem1%s%s where s_suppkey = l_suppkey LIMIT 30000;" % (sch_val, val, sch_val, val))
        elif str(sys.argv[3]) == 'Q2':
            # Q2 - TPCH
            queries.append("select * from part1%s%s, supplier1%s%s, partsupp1%s%s where p_partkey = ps_partkey and s_suppkey = ps_suppkey LIMIT 8000;" % (sch_val, val, sch_val, val, sch_val, val))
        elif str(sys.argv[3]) == 'Q3':
            # Q3 - TPCH
            queries.append("select * from customer1%s%s, order1%s%s, lineitem1%s%s where c_custkey = o_custkey and o_orderkey = l_orderkey LIMIT 30000;" % (sch_val, val, sch_val, val, sch_val, val))
        elif str(sys.argv[3]) == 'Q5':
            # Q5 - TPCH Modified
            queries.append("select * from lineitem1%s%s, order1%s%s, supplier1%s%s where o_orderkey = l_orderkey and s_suppkey = l_suppkey LIMIT 30000;" % (sch_val, val, sch_val, val, sch_val, val))
        elif str(sys.argv[3]) == 'Q8':
            # Q8 - TPCH Modified
            queries.append("select * from part1%s%s, supplier1%s%s, lineitem1%s%s where p_partkey = l_partkey and s_suppkey = l_suppkey LIMIT 60000;" % (sch_val, val, sch_val, val, sch_val, val))
        elif str(sys.argv[3]) == 'Q9_3R':
            # Q9_3R - TPCH Modified
            queries.append("select * from part1%s%s, partsupp1%s%s, lineitem1%s%s where ps_partkey = l_partkey and p_partkey = l_partkey LIMIT 200000;" % (sch_val, val, sch_val, val, sch_val, val))
        else:
            sys.exit(1)
    return queries


# Process for join query
def join_query(server_cur, log, itersize):
    # Fetch the result
    factor = SIGMA
    start_time = time()
    prev_time = start_time
    fetched_count = 0
    weighted_time = 0
    cumulative_time = 0
    idx = 0
    result = []
    
    for _ in server_cur:
        fetched_count += 1
        current_time = time()
        weighted_time += (current_time - prev_time) * factor
        prev_time = current_time
        factor *= SIGMA
        
        if fetched_count % itersize == 0:
            cumulative_time = time() - start_time
            if fetched_count >= data_points[idx]:
                log.write("%d, %f, %f\n"% (fetched_count, cumulative_time, weighted_time))
                result.append((fetched_count, cumulative_time, weighted_time))
                idx += 1
            if (cumulative_time >= TIME_LIMIT) or (idx >= DATA_LIMIT):
                break
            
    # Print the result
    print("Join time: {}s".format(cumulative_time))
    log.write("Total joined tuples fetched: %d\n" % (fetched_count))
    log.write('Time of current query run: %.2f sec\n' % (cumulative_time) + '\n')
    return result


# Manage a server-side cursor
def cursor_server(conn, Query):
    print("Executing query:" + Query)
    with open(result_log, 'a') as log:
        log.write("======================================================== \n")
        log.write("Time of the test run: " + str(datetime.datetime.now()) + '\n')
        
        test_results = []
        for i in range(TEST_NUMBER):
            
            log.write(Query + " #" + str(i + 1) + '\n')
            # Create a server-side cursor object
            with conn.cursor(name='cur_uniq') as server_cur:
                # Set the number of rows per a round trip with the server
                server_cur.itersize = ITER_SIZE

                print("Executing the query for the " + str(i + 1) + "-th time")
                start_time = time()
                # Execute the query
                server_cur.execute(Query)
                
                # Process for join query
                log.write("  Time before executing: %f sec\n" % (time() - start_time))
                result = join_query(server_cur, log, ITER_SIZE)
            test_results.append(result)
    return test_results


# Summarize results over multiple tests
def summary_tests(summary, test_results, Query):
    summary.write("\tQuery: %s\n" % (Query))
    
    minLenRun = sys.maxsize
    for i in range(len(test_results)):
        minLenRun = min(minLenRun, len(test_results[i]))

    avg_test_results = {}
    for j in range(minLenRun):
        unweighted_sum = 0
        weighted_sum = 0
        for i in range(len(test_results)):
            unweighted_sum += test_results[i][j][1]
            weighted_sum += test_results[i][j][2]
        tuples = test_results[i][j][0]
        avg_unweighted_time = unweighted_sum / len(test_results)
        avg_weighted_time = weighted_sum / len(test_results)
        summary.write("K val:%i\tExecution time (unweighted): %f\tExecution time (weighted): %f\n"
                      % (tuples, avg_unweighted_time, avg_weighted_time))
        
        if tuples not in avg_test_results:
            avg_test_results[tuples] = {}
            avg_test_results[tuples]['unweighted'] = []
            avg_test_results[tuples]['weighted'] = []
        avg_test_results[tuples]['unweighted'].append(avg_unweighted_time)
        avg_test_results[tuples]['weighted'].append(avg_weighted_time)
    summary.write("\n")
    return avg_test_results


# Summarize results over different queries
def summary_queries(summary, avg_results):
    summary.write("\n-- Average Execution Times Across Queries: A Summary --\n")
    with open(result_data_unweight, 'w+') as data_unweight, open(result_data_weight, 'w+') as data_weight:
        for k in sorted(avg_results.keys()):
            if len(avg_results[k]['unweighted']) >= 2:
                avg_unweighted = sum(avg_results[k]['unweighted']) / len(avg_results[k]['unweighted']) if avg_results[k]['unweighted'] else 0
                avg_weighted = sum(avg_results[k]['weighted']) / len(avg_results[k]['weighted']) if avg_results[k]['weighted'] else 0
                # Updated format
                summary.write("K val:%i\tAverage time (unweighted): %f\tAverage time (weighted): %f\n" % (k, avg_unweighted, avg_weighted))
                data_unweight.write("%i\t %f\n" % (k, avg_unweighted))
                data_weight.write("%i\t %f\n" % (k, avg_weighted))
            else:
                break

# Merge the results
def merge_dicts(d1, d2, option='intersection'):
    result = {}

    if option == 'union':
        keys = set(d1.keys()).union(d2.keys())
    else:
        keys = set(d1.keys()).intersection(d2.keys())

    for key in keys:
        if key in d1 and key in d2:
            if isinstance(d1[key], dict) and isinstance(d2[key], dict):
                result[key] = merge_dicts(d1[key], d2[key])
            else:
                result[key] = d1[key] + d2[key]
        elif key in d1:
            result[key] = d1[key]
        else:
            result[key] = d2[key]
    return result


# The main code
if __name__ == '__main__':
    # Create SQL query
    Queries = construct_join_queries(Z_VALAUE)
    summary = open(result_summary, 'w+')
    
    try:
        #conn = psycopg2.connect(dbname=DATABASE, user=USER, host=HOST, port=PORT)
        #conn.autocommit = True

        for retries_global in range(MAX_GLOBAL_RETRIES):
            try:
                # Connect to your PostgreSQL database
                with psycopg2.connect(dbname=DATABASE, user=USER, host=HOST, port=PORT) as conn:
                    avg_results, summary_results = {}, {}  # Reset results
                    
                    # Create a client-side cursor object
                    with conn.cursor() as cur:
                        # Apply settings
                        for setting in settings:
                            cur.execute(setting)

                        # Create a server-side cursor object
                        for Query in Queries:
                            results = cursor_server(conn, Query)
                            summary_results = summary_tests(summary, results, Query)

                            if (not avg_results) or (retries_global == MAX_GLOBAL_RETRIES - 1):
                                avg_results = merge_dicts(avg_results, summary_results, 'union')
                            else:
                                diff = abs(len(avg_results) - len(summary_results))
                                if diff <= 2:
                                    avg_results = merge_dicts(avg_results, summary_results)
                                else:
                                    # Raise an exception to restart from the beginning
                                    raise Exception("Results differ significantly restart from beginning")  
                            
                    # The test is done, summarize the results
                    summary_queries(summary, avg_results)
                    break

            except Exception as e:
                print(e)
            finally:
                # Close the connection
                if conn:
                    conn.close()
                
        if retries_global == MAX_GLOBAL_RETRIES - 1:
            print("\nMax global retries reached for query, stopping.")

    finally:
        # Close the connection
        if conn:
            conn.close()
        if summary:
            summary.flush()
            summary.close()
        print("The test is finished.\n")
