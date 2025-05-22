# Divergent Association Task (DAT) score CSV calculator

This project computes a creativity score for each row in a CSV file using the Divergent Association Task (DAT) model. The DAT model measures creativity by analyzing the semantic distance between words provided in a specific column of your CSV file (default column: `test`).

- The script reads your CSV file, extracts the words from the specified column, and uses a pre-trained GloVe word embedding model to compute the semantic distances between the words.
- If there are at least 7 valid words in the row, the script calculates the average semantic distance (the DAT score) and writes it to a new column in the output CSV file.
- If there are not enough valid words, the script notes this in the output.
- The output CSV file will have the same data as the input, with an additional column containing the creativity score for each row.

This approach leverages natural language processing and vectorized operations (via NumPy) for efficient computation. The DAT model and methodology are based on research published in PNAS: [Naming unrelated words predicts creativity](https://www.pnas.org/content/118/25/e2022340118).

## Setup Instructions

1. **Install Python 3 and Poetry:**
   - Download and install [Python 3](https://www.python.org/downloads/).
   - Install [Poetry](https://python-poetry.org/docs/#installation).

2. **Install dependencies:**
   ```sh
   poetry install
   ```

3. **Download GloVe model:**
   - Download `glove.840B.300d.zip` from [GloVe Project Page](https://nlp.stanford.edu/projects/glove/).
   - Place `glove.840B.300d.zip` in the `word_vector/` directory.
   - Unzip it so that `glove.840B.300d.txt` is also in `word_vector/`.

4. **Run the script:**
   ```sh
   poetry run python main.py <csv_file_path>
   ```
   - Replace `<csv_file_path>` with the path to your input CSV file.

5. **Run unit tests:**
   ```sh
   poetry run pytest test_main.py
   ```

## Notes
- The script expects a column named `test` in your CSV file by default. Adjust `NOUNS_HEADER` in `main.py` if needed.
- The GloVe model is large (~2GB). Ensure you have enough disk space.
- For more details, see `dat_src/README.md`.
