import pandas as pd
from flask import Flask, jsonify, request, send_file,render_template_string
import os
import sqlite3

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Connect to the SQLite database
conn = sqlite3.connect('data.db', check_same_thread=False)
c = conn.cursor()

@app.route('/upload', methods=['GET'])
def upload_form():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>CSV File Upload</title>
    </head>
    <body>
        <h1>Upload a CSV File</h1>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept=".csv" required>
            <button type="submit">Upload</button>
        </form>
    </body>
    </html>
    ''')

@app.route('/upload', methods=['POST'])
def upload_csv():
    file = request.files['file']
    if file:
        try:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            table_name = f"table_{filename.replace('.', '_')}"
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            return jsonify({'message': 'CSV file uploaded and stored in the database successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': 'No file provided'}), 400

@app.route('/get', methods=['GET'])
def get_row():
    dataset = request.args.get('dataset')
    if dataset:
        table_name = f"table_{dataset.replace('.', '_')}"
        filters = {col: request.args.get(col) for col in get_columns(table_name)}
        query = f"SELECT * FROM {table_name} WHERE "
        conditions = []
        for col, value in filters.items():
            if value:
                conditions.append(f"{col}='{value}'")
        query += " AND ".join(conditions)
        c.execute(query)
        result = c.fetchall()
        if len(result) == 1:
            return jsonify(dict(zip([column[0] for column in c.description], result[0]))), 200
        elif len(result) > 1:
            return jsonify({'error': 'Multiple rows found with the given filters'}), 400
        else:
            return jsonify({'error': 'No row found with the given filters'}), 404
    else:
        return jsonify({'error': 'Please provide a dataset parameter'}), 400

@app.route('/search', methods=['GET'])
def search_rows():
    dataset = request.args.get('dataset')
    keyword = request.args.get('q')
    if dataset and keyword:
        table_name = f"table_{dataset.replace('.', '_')}"
        columns = get_columns(table_name)
        query = f"SELECT * FROM {table_name} WHERE "
        conditions = [f"{col} LIKE '%{keyword}%'" for col in columns]
        query += " OR ".join(conditions)
        c.execute(query)
        result = c.fetchall()
        rows = []
        for row in result:
            rows.append(dict(zip([column[0] for column in c.description], row)))
        return jsonify(rows), 200
    else:
        return jsonify({'error': 'Please provide dataset and keyword parameters'}), 400

def get_columns(table_name):
    c.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in c.fetchall()]
    return columns

if __name__ == '__main__':
    app.run(debug=True)