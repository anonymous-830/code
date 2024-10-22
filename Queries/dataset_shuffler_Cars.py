# !/bin/python
from __future__ import print_function
import datetime
import psycopg2
from time import time
from time import sleep
import sys

def main():
    shuffles = ['1', '2', '3']
    # Open connection
    conn = psycopg2.connect(host="XXXX", database="XXXX", user="XXXX", port="XXXX")
    cur = conn.cursor()
    # If only one argument, clean is provided, drop and remake tables, then exit
    if len(sys.argv) == 2 and sys.argv[1] == "clean":
        createTables(shuffles, conn)
        exit()

def makeCopyString(scf, table):
    print("Time of data reload start: " + str(datetime.datetime.now()))
    # Ensure only entries with a non-null brand are selected and copied
    query = "INSERT INTO {}{} SELECT * FROM {} ORDER BY RANDOM();".format(table, scf, table)
    return query

def createTables(shuffles, conn):
    cur = conn.cursor()
    try:
        for scf in shuffles:
            print("Recreating shuffle: {}".format(scf))
            cur.execute("DROP TABLE IF EXISTS Car_brands" + scf + ";")
            cur.execute("DROP TABLE IF EXISTS parking_tickets" + scf + ";")

            cur.execute("CREATE TABLE Car_brands" + scf + """ (
                                                        Year INT,
                                                        Make TEXT,
                                                        Model TEXT,
                                                        Category TEXT
                                                    );""")
            cur.execute("CREATE TABLE parking_tickets" + scf + """ (
                                                        summons_number BIGINT PRIMARY KEY,
                                                        plate_id TEXT,
                                                        registration_state TEXT,
                                                        plate_type TEXT,
                                                        issue_date DATE,
                                                        violation_code INT,
                                                        vehicle_body_type TEXT,
                                                        vehicle_make TEXT,
                                                        violation_location TEXT,
                                                        violation_precinct INT,
                                                        vehicle_color TEXT
                                                    );""")

            # Execute and commit data copy for wdc1 and wdc2
            cur.execute(makeCopyString(scf, "Car_brands"))
            cur.execute(makeCopyString(scf, "parking_tickets"))
            conn.commit()
            print("Data loaded successfully for shuffle {}.".format(scf))
    except Exception as e:
        print("An error occurred: {}".format(e))
        conn.rollback()  # Rollback in case of error
        raise  # Optionally re-raise the error after handling
    print('Cars done')


if __name__ == '__main__':
    main()
