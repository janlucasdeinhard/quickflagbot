from flask import Flask, render_template, request, jsonify
import sqlite3
import pandas as pd

app = Flask(__name__)

def get_data(selected_ids=None):
    conn = sqlite3.connect("sample_crm.db")
    df = pd.read_sql("SELECT * FROM test_results_aggregated", conn)
    conn.close()
    if selected_ids:
        df = df[df['sql_query_id'].isin(selected_ids)]
    # Calculate pass percentage per test per timestamp
    df_pivot = df.pivot_table(index=['sql_query_id', 'timestamp'], columns='test_result', values='count', fill_value=0)
    df_pivot['pass_rate'] = df_pivot.get('PASS', 0) / (df_pivot.get('PASS', 0) + df_pivot.get('FAIL', 0))
    df_pivot = df_pivot.reset_index()
    return df_pivot

@app.route('/')
def index():
    conn = sqlite3.connect("sample_crm.db")
    ids = pd.read_sql("SELECT DISTINCT sql_query_id FROM test_results_aggregated", conn)['sql_query_id'].tolist()
    conn.close()
    return render_template('dashboard.html', ids=ids)

@app.route('/api/data')
def api_data():
    ids = request.args.getlist('ids')
    data = get_data(ids if ids else None)
    return jsonify(data.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)