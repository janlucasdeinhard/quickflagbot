import sqlite3
import os
import pandas as pd
import datetime

def run_all_tests_and_aggregate(
    db_path,
    tests_folder="tests/generated",
    table_name="test_results_aggregated"
):
    """
    Runs all SQL test files in the specified folder against the given SQLite database,
    aggregates the results, and writes them to the database table (appending if exists, creating if not).
    Each test result is timestamped and labeled with the test name.

    Args:
        db_path (str): Path to the SQLite database file.
        tests_folder (str): Path to the folder containing .sql test files.
        table_name (str): Name of the table to store aggregated results.

    Returns:
        pd.DataFrame: Aggregated results DataFrame.
    """
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch all SQL queries from tests folder into a dictionary
    sql_dict = {}
    for filename in os.listdir(tests_folder):
        if filename.endswith(".sql"):
            with open(os.path.join(tests_folder, filename), "r") as f:
                sql = f.read()
            sql_dict[filename.replace('.sql','')] = sql

    # Evaluate all SQL queries and store results in a dictionary of DataFrames
    sql_res_dict = {}
    for sql_query_id in sql_dict.keys():
        cursor.execute(sql_dict[sql_query_id])
        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        df = pd.DataFrame(results, columns=columns)
        sql_res_dict[sql_query_id] = df

    # Aggregate the evaluation results and attach timestamp and name of test
    rf = pd.DataFrame(columns=['sql_query_id','timestamp','test_result','count'])
    for sql_query_id in sql_res_dict.keys():
        df = sql_res_dict[sql_query_id]
        df = pd.DataFrame(['PASS','FAIL'],columns=['test_result']).merge(
            df.groupby(['test_result']).size().reset_index(name='count'),
            on='test_result',
            how='left'
        ).fillna(0).assign(timestamp=datetime.datetime.now().isoformat()).assign(sql_query_id=sql_query_id)
        df = df[['sql_query_id','timestamp','test_result','count']]
        rf = pd.concat([rf, df], ignore_index=True)

    # Check if table exists and write/append
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    exists = cursor.fetchone() is not None
    if exists:
        rf.to_sql(table_name, conn, if_exists='append', index=False)
    else:
        rf.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    return

# Example usage:
if __name__ == '__main__':
    run_all_tests_and_aggregate(
        db_path="sample_crm.db",
        tests_folder="tests/generated",
        table_name="test_results_aggregated"
    )