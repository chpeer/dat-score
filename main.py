"""
Main module for the creativity_score project.
"""

import csv
import sys
from dat import Model

NOUNS_HEADER: str = 'test'
CREATIVITY_SCORE_HEADER: str = f'{NOUNS_HEADER}_hello'
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
            dictionary="dat_src/words.txt"
        )
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile, \
             open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
            reader = csv.reader(csvfile)
            writer = csv.writer(outfile)
            header = next(reader)
            if NOUNS_HEADER not in header:
                print(f"Column '{NOUNS_HEADER}' not found in CSV header.")
                return
            nouns_col_idx = header.index(NOUNS_HEADER)
            # Write new header with additional column
            writer.writerow(header + [CREATIVITY_SCORE_HEADER])
            for row in reader:
                # Compute creativity score using dat_model.dat
                if len(row) > nouns_col_idx:
                    # Split the cell into words (space-separated)
                    nouns = row[nouns_col_idx].split()
                    try:
                        score = dat_model.dat(nouns, minimum=MIN_WORD_COUNT)
                        if score is None:
                            print(f"Not enough valid words in row: {row}")
                            new_value = 'not enough words'
                        else:
                            new_value = str(score)
                    except Exception as e:
                        new_value = f'error: {e}'
                else:
                    new_value = ''
                writer.writerow(row + [new_value])
        print(f"Output written to {output_path}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()

