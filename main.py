"""
Flask web server for DAT score calculation with interactive column selection and minimum word count.
"""
import os
import csv
import tempfile
import logging
from flask import Flask, request, send_file, render_template_string, redirect, url_for, session
from dat import Model
import prod_config

app = Flask(__name__)
app.config.from_object('prod_config')

# Configure proxy support
if app.config.get('PROXY_FIX', False):
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.secret_key = os.environ.get('SECRET_KEY', 'dev-placeholder-key')  # Needed for session

# Enforce HTTPS in production
# @app.before_request
# def enforce_https():
#     if not request.is_secure and not app.debug:
#         url = request.url.replace('http://', 'https://', 1)
#         return redirect(url, code=301)

# Initialize DAT model at server start
logging.basicConfig(level=logging.INFO)
logging.info("Starting DAT Score Calculator application...")
logging.info("Loading DAT model from word vectors...")
DAT_MODEL = Model(
    model="word_vector/glove.840B.300d.txt",
    dictionary="word_vector/words.txt"
)
logging.info("DAT model loaded successfully.")

UPLOAD_FORM = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DAT Score Calculator</title>
  <link rel="stylesheet" href="/static/dat_score_app.css">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&display=swap">
</head>
<body>
  <div class="container">
    <header class="app-header">
      <div class="header-content">
        <svg class="header-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M3 13h6v8H3v-8zM9 3h6v18H9V3zm6 8h6v10h-6V11z" fill="currentColor"/>
        </svg>
        <h1 class="app-title">DAT Score Calculator</h1>
      </div>
    </header>
    
    <main class="main-content">
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Upload CSV File</h2>
          <p class="card-subtitle">Upload your CSV file to begin calculating creativity scores</p>
        </div>
        
        <div class="card-content">
          <form method="post" enctype="multipart/form-data" class="upload-form">
            <div class="form-group">
              <label for="file" class="form-label">CSV File</label>
              <div class="file-input-container">
                <input type="file" name="file" id="file" accept=".csv" class="file-input" required>
                <label for="file" class="file-input-label">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M14 2V8H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M16 13H8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M16 17H8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M10 9H8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>Choose a CSV file</span>
                </label>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="submit" class="btn btn-primary">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2L12 16M12 2L8 6M12 2L16 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M20 12V18C20 19.1046 19.1046 20 18 20H6C4.89543 20 4 19.1046 4 18V12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Upload File
              </button>
            </div>
          </form>
        </div>
      </div>
    </main>
  </div>
</body>
</html>
'''

SELECT_FORM = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Select Columns - DAT Score Calculator</title>
  <link rel="stylesheet" href="/static/dat_score_app.css">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&display=swap">
  <script>
    function updatePreview() {
      document.getElementById('action').value = 'preview';
      document.getElementById('select-form').submit();
    }
  </script>
</head>
<body>
  <div class="container">
    <header class="app-header">
      <div class="header-content">
        <svg class="header-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M3 13h6v8H3v-8zM9 3h6v18H9V3zm6 8h6v10h-6V11z" fill="currentColor"/>
        </svg>
        <h1 class="app-title">DAT Score Calculator</h1>
      </div>
    </header>
    
    <main class="main-content">
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Select Columns for DAT Calculation</h2>
          <p class="card-subtitle">Choose which columns to use for creativity score calculation</p>
        </div>
        
        <div class="card-content">
          <form method="post" action="{{ url_for('select_columns') }}" id="select-form" class="select-form">
            <div class="form-group">
              <label for="columns" class="form-label">Select columns to use as words</label>
              <p class="form-hint">Hold Ctrl to select multiple, hold Shift to select range</p>
              <select name="columns" id="columns" multiple size="10" required class="form-select">
                {% for col in columns %}
                  <option value="{{ col }}">{{ col }}</option>
                {% endfor %}
              </select>
            </div>
            <div class="form-row form-row-inline">
              <div class="form-group form-group-small">
                <label for="min_word_count" class="form-label">Min words</label>
                <input type="number" name="min_word_count" id="min_word_count" value="7" min="1" max="20" class="form-input form-input-small">
              </div>
              <div class="form-group form-group-small">
                <label for="skip_rows" class="form-label">Rows to skip</label>
                <input type="number" name="skip_rows" id="skip_rows" value="{{ skip_rows }}" min="0" max="100" class="form-input form-input-small" onchange="updatePreview()">
              </div>
              <div class="form-actions form-actions-inline">
                <button type="submit" name="action" value="Calculate Score" class="btn btn-primary btn-inline">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  Calculate Score
                </button>
              </div>
            </div>
            <input type="hidden" name="action" id="action" value="">
          </form>
        </div>
      </div>
      
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Preview of Uploaded Data</h2>
        </div>
        <div class="card-content">
          <div class="table-scroll">
            <table class="dat-table">
              <thead>
                <tr>{% for col in columns %}<th>{{ col }}</th>{% endfor %}</tr>
              </thead>
              <tbody>
              {% for row in rows %}
                <tr>
                  {% for cell in row %}<td>{{ cell }}</td>{% endfor %}
                </tr>
              {% endfor %}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>
  </div>
</body>
</html>
'''

RESULTS_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Results - DAT Score Calculator</title>
  <link rel="stylesheet" href="/static/dat_score_app.css">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&display=swap">
</head>
<body>
  <div class="container">
    <header class="app-header">
      <div class="header-content">
        <svg class="header-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M3 13h6v8H3v-8zM9 3h6v18H9V3zm6 8h6v10h-6V11z" fill="currentColor"/>
        </svg>
        <h1 class="app-title">DAT Score Calculator</h1>
      </div>
    </header>
    
    <main class="main-content">
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">DAT Score Results</h2>
          <p class="card-subtitle">Your creativity scores have been calculated successfully</p>
        </div>
        
        <div class="card-content">
          <div class="button-container">
            <form method="get" action="{{ url_for('download') }}" style="display: inline;">
              <button type="submit" class="btn btn-primary">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2L12 16M12 2L8 6M12 2L16 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M20 12V18C20 19.1046 19.1046 20 18 20H6C4.89543 20 4 19.1046 4 18V12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Download Results as CSV
              </button>
            </form>
            <a href="{{ url_for('upload_file') }}" class="btn btn-secondary">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M1 4V10H7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M3.51 15A9 9 0 1 0 6 5L1 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              Start Over
            </a>
          </div>
        </div>
      </div>
      
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Results Table</h2>
        </div>
        <div class="card-content">
          <div class="table-scroll">
            <table class="dat-table">
              <thead>
                <tr>{% for col in columns %}<th>{{ col }}</th>{% endfor %}<th>{{ score_col }}</th></tr>
              </thead>
              <tbody>
              {% for row, score in results %}
                <tr>
                  {% for cell in row %}<td>{{ cell }}</td>{% endfor %}
                  <td class="score-cell">{{ score }}</td>
                </tr>
              {% endfor %}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>
  </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')
        skip_rows = int(request.form.get('skip_rows', 1))
        if not file or not getattr(file, 'filename', '').endswith('.csv'):
            logging.error('Please upload a CSV file.')
            return 'Please upload a CSV file.', 400
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_in:
            file.save(tmp_in)
            tmp_in_path = tmp_in.name
        # Read header and preview rows
        with open(tmp_in_path, newline='', encoding='utf-8') as f:
            reader = list(csv.reader(f))
            if len(reader) <= skip_rows:
                header = reader[0] if reader else []
                preview_rows = []
            else:
                header = reader[0]
                preview_rows = reader[skip_rows:skip_rows+10]
        session['tmp_in_path'] = tmp_in_path
        session['header'] = header
        session['skip_rows'] = skip_rows
        return render_template_string(SELECT_FORM, columns=header, rows=preview_rows, skip_rows=skip_rows)
    return render_template_string(UPLOAD_FORM)

@app.route('/select', methods=['POST'])
def select_columns():
    columns = request.form.getlist('columns')
    min_word_count = int(request.form.get('min_word_count', 7))
    skip_rows = int(request.form.get('skip_rows', 1))
    tmp_in_path = session.get('tmp_in_path')
    header = session.get('header')
    session['skip_rows'] = skip_rows
    # Fix: allow preview to work even if columns is empty (user hasn't selected yet)
    if (request.form.get('action') == 'preview') and (tmp_in_path is not None and header is not None):
        if not os.path.exists(tmp_in_path):
            logging.error('The uploaded file is no longer available. Please re-upload your CSV file.')
            return 'The uploaded file is no longer available. Please re-upload your CSV file.', 400
        with open(tmp_in_path, newline='', encoding='utf-8') as f:
            reader = list(csv.reader(f))
            file_header = reader[0]
            all_rows = reader[1:]
            rows = all_rows[skip_rows-1:] if skip_rows > 0 else all_rows
        preview_rows = rows[:10]
        return render_template_string(SELECT_FORM, columns=header, rows=preview_rows, skip_rows=skip_rows)
    if not columns or tmp_in_path is None or header is None:
        logging.error('Session expired or invalid. Please re-upload your CSV file.')
        return 'Session expired or invalid. Please re-upload your CSV file.', 400
    if not os.path.exists(tmp_in_path):
        logging.error('The uploaded file is no longer available. Please re-upload your CSV file.')
        return 'The uploaded file is no longer available. Please re-upload your CSV file.', 400
    # Read all rows from file
    with open(tmp_in_path, newline='', encoding='utf-8') as f:
        reader = list(csv.reader(f))
        file_header = reader[0]
        all_rows = reader[1:]
        rows = all_rows[skip_rows-1:] if skip_rows > 0 else all_rows
    # Calculate scores using global DAT_MODEL
    col_indices = [header.index(col) for col in columns]
    results = []
    score_col = 'creativity_score'
    for row in rows:
        nouns = [row[idx] for idx in col_indices if idx < len(row) and row[idx].strip()]
        try:
            score = DAT_MODEL.dat(nouns, minimum=min_word_count)
            if score is None:
                score_val = 'not enough words'
            else:
                score_val = str(score)
        except Exception as e:
            logging.error(f'Error calculating DAT score for row {row}: {e}')
            score_val = f'error: {e}'
        results.append((row, score_val))
    # Save results for download (include skipped rows at the top, unmodified)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w', newline='', encoding='utf-8') as tmp_out:
        writer = csv.writer(tmp_out)
        writer.writerow(header + [score_col])
        # Write skipped rows (without score column
        for i in range(skip_rows-1):
            if i < len(all_rows):
                writer.writerow(all_rows[i])
        # Write processed rows with score
        for row, score_val in results:
            writer.writerow(row + [score_val])
        session['tmp_out_path'] = tmp_out.name
    # Only display selected columns and the score in the results table
    display_indices = [header.index(col) for col in columns]
    display_columns = columns + [score_col]
    display_results = [([row[idx] for idx in display_indices], score_val) for row, score_val in results]
    return render_template_string(
        RESULTS_TEMPLATE,
        columns=columns,
        results=display_results,
        score_col=score_col
    )

@app.route('/download')
def download():
    tmp_out_path = session.get('tmp_out_path')
    if not tmp_out_path or not os.path.exists(tmp_out_path):
        return redirect(url_for('upload_file'))
    return send_file(tmp_out_path, as_attachment=True, download_name='output_creativity_score.csv')

if __name__ == '__main__':
    app.run(debug=True)

