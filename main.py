"""
Flask web server for DAT score calculation.
"""
import os
import csv
import tempfile
from flask import Flask, request, send_file, render_template_string
from dat import Model

NOUNS_HEADERS: list[str] = [f'DAT_{i}' for i in range(1, 11)]
CREATIVITY_SCORE_HEADER: str = 'creativity_score'
MIN_WORD_COUNT: int = 7

app = Flask(__name__)

UPLOAD_FORM = '''
<!doctype html>
<title>DAT Score Calculator</title>
<h1>Upload CSV File</h1>
<form method=post enctype=multipart/form-data>
  <input type=file name=file accept=".csv">
  <input type=submit value=Upload>
</form>
'''

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or not file.filename.endswith('.csv'):
            return 'Please upload a CSV file.', 400
        # Save uploaded file to a temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_in:
            file.save(tmp_in)
            tmp_in_path = tmp_in.name
        tmp_out_path = tmp_in_path.replace('.csv', '_creativity_score.csv')
        # Process file
        try:
            dat_model = Model(
                model="word_vector/glove.840B.300d.txt",
                dictionary="word_vector/words.txt"
            )
            with open(tmp_in_path, mode='r', newline='', encoding='utf-8') as csvfile, \
                 open(tmp_out_path, mode='w', newline='', encoding='utf-8') as outfile:
                reader = csv.reader(csvfile)
                writer = csv.writer(outfile)
                header = next(reader)
                if not all(col in header for col in NOUNS_HEADERS):
                    return f"One or more DAT columns ({NOUNS_HEADERS}) not found in CSV header.", 400
                nouns_col_indices = [header.index(col) for col in NOUNS_HEADERS]
                writer.writerow(header + [CREATIVITY_SCORE_HEADER])
                # Write metadata rows (rows 2 and 3) unchanged
                for _ in range(2):
                    try:
                        metadata_row = next(reader)
                        writer.writerow(metadata_row + [''])
                    except StopIteration:
                        break
                for row in reader:
                    nouns = [row[idx] for idx in nouns_col_indices if idx < len(row) and row[idx].strip()]
                    try:
                        score = dat_model.dat(nouns, minimum=MIN_WORD_COUNT)
                        if score is None:
                            new_value = 'not enough words'
                        else:
                            new_value = str(score)
                    except Exception as e:
                        new_value = f'error: {e}'
                    writer.writerow(row + [new_value])
            return send_file(tmp_out_path, as_attachment=True, download_name='output_creativity_score.csv')
        finally:
            if os.path.exists(tmp_in_path):
                os.remove(tmp_in_path)
            # Do not remove tmp_out_path here, let send_file handle it
    return render_template_string(UPLOAD_FORM)

if __name__ == '__main__':
    app.run(debug=True)

