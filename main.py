"""
Flask web server for DAT score calculation with interactive column selection and minimum word count.
"""
import os
import csv
import tempfile
from flask import Flask, request, send_file, render_template_string, redirect, url_for, session
from dat import Model

app = Flask(__name__)
app.secret_key = 'dat_secret_key'  # Needed for session

UPLOAD_FORM = '''
<!doctype html>
<title>DAT Score Calculator</title>
<h1>Upload CSV File</h1>
<form method=post enctype=multipart/form-data>
  <input type=file name=file accept=".csv">
  <input type=submit value=Upload>
</form>
'''

SELECT_FORM = '''
<!doctype html>
<title>Select Columns</title>
<h1>Select Columns for DAT Calculation</h1>
<form method=post action="{{ url_for('select_columns') }}">
  <label for="columns">Select columns to use as words (hold Ctrl to select multiple):</label><br>
  <select name="columns" id="columns" multiple size="10" required>
    {% for col in columns %}
      <option value="{{ col }}">{{ col }}</option>
    {% endfor %}
  </select><br><br>
  <label for="min_word_count">Minimum word count:</label>
  <input type="number" name="min_word_count" id="min_word_count" value="7" min="1" max="20"><br><br>
  <input type="submit" value="Calculate Score">
</form>
<h2>Preview of Uploaded Data</h2>
<table border=1>
  <tr>{% for col in columns %}<th>{{ col }}</th>{% endfor %}</tr>
  {% for row in rows[:10] %}
    <tr>{% for cell in row %}<td>{{ cell }}</td>{% endfor %}</tr>
  {% endfor %}
</table>
'''

RESULTS_TEMPLATE = '''
<!doctype html>
<title>DAT Score Results</title>
<h1>DAT Score Results</h1>
<form method="get" action="{{ url_for('download') }}">
  <button type="submit">Download Results as CSV</button>
</form>
<br>
<table border=1>
  <tr>{% for col in columns %}<th>{{ col }}</th>{% endfor %}<th>{{ score_col }}</th></tr>
  {% for row, score in results %}
    <tr>{% for cell in row %}<td>{{ cell }}</td>{% endfor %}<td>{{ score }}</td></tr>
  {% endfor %}
</table>
'''

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or not file.filename.endswith('.csv'):
            return 'Please upload a CSV file.', 400
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_in:
            file.save(tmp_in)
            tmp_in_path = tmp_in.name
        # Read header and preview rows
        with open(tmp_in_path, newline='', encoding='utf-8') as f:
            reader = list(csv.reader(f))
            header = reader[0]
            preview_rows = reader[1:11]  # Only preview first 10 rows
        session['tmp_in_path'] = tmp_in_path
        session['header'] = header
        # Do NOT store all rows in session
        return render_template_string(SELECT_FORM, columns=header, rows=preview_rows)
    return render_template_string(UPLOAD_FORM)

@app.route('/select', methods=['POST'])
def select_columns():
    columns = request.form.getlist('columns')
    min_word_count = int(request.form.get('min_word_count', 7))
    tmp_in_path = session.get('tmp_in_path')
    header = session.get('header')
    if not columns or tmp_in_path is None or header is None:
        return 'Session expired or invalid. Please re-upload your CSV file.', 400
    if not os.path.exists(tmp_in_path):
        return 'The uploaded file is no longer available. Please re-upload your CSV file.', 400
    # Read all rows from file
    with open(tmp_in_path, newline='', encoding='utf-8') as f:
        reader = list(csv.reader(f))
        file_header = reader[0]
        rows = reader[1:]
    # Calculate scores
    dat_model = Model(
        model="word_vector/glove.840B.300d.txt",
        dictionary="word_vector/words.txt"
    )
    col_indices = [header.index(col) for col in columns]
    results = []
    score_col = 'creativity_score'
    for row in rows:
        nouns = [row[idx] for idx in col_indices if idx < len(row) and row[idx].strip()]
        try:
            score = dat_model.dat(nouns, minimum=min_word_count)
            if score is None:
                score_val = 'not enough words'
            else:
                score_val = str(score)
        except Exception as e:
            score_val = f'error: {e}'
        results.append((row, score_val))
    # Save results for download
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w', newline='', encoding='utf-8') as tmp_out:
        writer = csv.writer(tmp_out)
        writer.writerow(header + [score_col])
        for row, score_val in results:
            writer.writerow(row + [score_val])
        session['tmp_out_path'] = tmp_out.name
    return render_template_string(RESULTS_TEMPLATE, columns=header, results=results, score_col=score_col)

@app.route('/download')
def download():
    tmp_out_path = session.get('tmp_out_path')
    if not tmp_out_path or not os.path.exists(tmp_out_path):
        return redirect(url_for('upload_file'))
    return send_file(tmp_out_path, as_attachment=True, download_name='output_creativity_score.csv')

if __name__ == '__main__':
    app.run(debug=True)

