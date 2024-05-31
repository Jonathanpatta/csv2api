import pandas as pd
from flask import Flask, jsonify, request, send_file
import os

app = Flask(__name__)

# Global variable to store the loaded DataFrame
df = None

@app.route('/upload', methods=['POST'])
def upload_csv():
    global df
    file = request.files['file']
    if file:
        try:
            df = pd.read_csv(file)
            return jsonify({'message': 'CSV file uploaded successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': 'No file provided'}), 400

@app.route('/get', methods=['GET'])
def get_row():
    if df is None:
        return jsonify({'error': 'No CSV file uploaded yet'}), 400

    filters = {col: request.args.get(col) for col in df.columns}
    filtered_df = df.copy()

    for col, value in filters.items():
        if value:
            filtered_df = filtered_df[filtered_df[col] == value]

    if len(filtered_df) == 1:
        return jsonify(filtered_df.to_dict('records')[0]), 200
    elif len(filtered_df) > 1:
        return jsonify({'error': 'Multiple rows found with the given filters'}), 400
    else:
        return jsonify({'error': 'No row found with the given filters'}), 404

@app.route('/search', methods=['GET'])
def search_rows():
    if df is None:
        return jsonify({'error': 'No CSV file uploaded yet'}), 400

    keyword = request.args.get('keyword')
    if keyword:
        filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1)]
        return jsonify(filtered_df.to_dict('records')), 200
    else:
        return jsonify({'error': 'Please provide a keyword parameter'}), 400

@app.route('/download', methods=['GET'])
def download_csv():
    if df is None:
        return jsonify({'error': 'No CSV file uploaded yet'}), 400

    csv_file = 'temp.csv'
    df.to_csv(csv_file, index=False)
    return send_file(csv_file, as_attachment=True, download_name='data.csv'), 200

if __name__ == '__main__':
    app.run(debug=True)