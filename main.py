"""
Main module for the creativity_score project.
"""

import csv
import sys
from dat import Model

NOUNS_HEADERS: list[str] = [f'DAT_{i}' for i in range(1, 11)]
CREATIVITY_SCORE_HEADER: str = 'creativity_score'
MIN_WORD_COUNT: int = 7


def main() -> None:
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <csv_file_path>")
        return
    file_path: str = sys.argv[1]
    output_path: str = f"{file_path.rsplit('.', 1)[0]}_creativity_score.csv"
    try:
        # Initialize the DAT model (requires GloVe and words.txt files in the correct location)
        dat_model = Model(
            model="word_vector/glove.840B.300d.txt",  # Updated path
            dictionary=".venv/src/divergent-association-task/words.txt"
        )
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile, \
             open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
            reader = csv.reader(csvfile)
            writer = csv.writer(outfile)
            header = next(reader)
            # Check all required DAT columns exist
            if not all(col in header for col in NOUNS_HEADERS):
                print(f"One or more DAT columns ({NOUNS_HEADERS}) not found in CSV header.")
                return
            # Get indices for DAT columns
            nouns_col_indices = [header.index(col) for col in NOUNS_HEADERS]
            # Write new header with additional column
            writer.writerow(header + [CREATIVITY_SCORE_HEADER])
            # Write metadata rows (rows 2 and 3) unchanged
            metadata_rows = []
            for _ in range(2):
                try:
                    metadata_row = next(reader)
                    writer.writerow(metadata_row + [''])
                except StopIteration:
                    break
            for row in reader:
                # Collect nouns from the DAT columns
                nouns = [row[idx] for idx in nouns_col_indices if idx < len(row) and row[idx].strip()]
                try:
                    score = dat_model.dat(nouns, minimum=MIN_WORD_COUNT)
                    if score is None:
                        print(f"Not enough valid words in row: {row}")
                        new_value = 'not enough words'
                    else:
                        new_value = str(score)
                    # Print nouns and creativity score to stdout
                    print(f"Nouns: {nouns} | Creativity Score: {new_value}")
                except Exception as e:
                    new_value = f'error: {e}'
                    print(f"Nouns: {nouns} | Creativity Score: {new_value}")
                writer.writerow(row + [new_value])
        print(f"Output written to {output_path}")
    except FileNotFoundError as e:
       # print(f"File not found: {file_path}")
       print(e)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()

