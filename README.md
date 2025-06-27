<!--
NOTE: This project was created with the assistance of AI. It is not intended for production use and must not be exposed to the internet. The server and code are not security-audited and may contain vulnerabilities. Use only in a safe, isolated environment for demonstration or research purposes.
-->
# DAT Score Web App

This project provides a web interface for calculating Divergent Association Task (DAT) creativity scores from CSV files using GloVe word vectors.

## Features
- Upload CSV files and preview data
- Select columns and set minimum word count for DAT calculation
- Set number of rows to skip (header/metadata)
- Calculate and download creativity scores
- Containerized deployment

## Requirements
- Docker (and optionally Docker Compose)
- Python 3.12+ (for local development)
- GloVe vectors and words list (see `word_vector/`)

  **Download GloVe:**
  - [GloVe 840B 300d (2.03 GB)](https://nlp.stanford.edu/data/glove.840B.300d.zip)
  - Unzip and place `glove.840B.300d.txt` and `words.txt` in the `word_vector/` directory.

## Quick Start (Production)

1. **Clone the repository and prepare word vectors**
   - Place your GloVe and words.txt files in the `word_vector/` directory.

2. **Build and run with Docker Compose**
   ```powershell
   docker compose up --build
   ```
   - The `word_vector/` folder is mounted into the container as a read-only volume.
   - The app will be available at http://localhost:8080

3. **Set your secret key**
   - Edit `docker-compose.yml` and set a strong value for `SECRET_KEY`.

## Local Development

1. **Install dependencies**
   ```powershell
   pip install poetry
   poetry install
   ```
2. **Run the app**
   ```powershell
   poetry run python main.py
   ```

## Project Structure
- `main.py` - Flask web server
- `word_vector/` - GloVe vectors and words.txt (required, not included in Docker image)
- `static/` - CSS for web UI
- `test_data/` - Example/test CSV files (not included in Docker image)
- `prod_config.py` - Production Flask config
- `Dockerfile` - Production container build (uses python:3.12-alpine, excludes word_vector)
- `docker-compose.yml` - Mounts word_vector as a volume, sets environment variables
- `.dockerignore`/`.gitignore` - Exclude dev, test, and large files from builds and git

## Security & Production Notes
- Only HTTPS is allowed in production (HTTP is redirected)
- All secrets (SECRET_KEY) must be set via environment variables
- Uploaded files are stored in secure temp locations
- The app is served by Waitress (WSGI) in production

## Running Tests
- Tests and test data are excluded from the Docker image.
- To run tests locally:
  ```powershell
  poetry run pytest
  ```

---

For more details, see comments in `main.py` and the configuration files.
