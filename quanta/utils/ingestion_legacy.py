import os
import gzip
import pandas as pd

# Base directory where Quanta's data is stored
BASE_DIR = '/data/polygon/stocks_trades/'

def find_all_gz_files(base_dir):
    """Find all .csv.gz files in the base directory."""
    all_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.csv.gz'):
                all_files.append(os.path.join(root, file))
    return all_files

def process_file(file_path):
    """Process a single .csv.gz file."""
    try:
        with gzip.open(file_path, 'rt') as f:
            df = pd.read_csv(f, nrows=5)  # Only read first 5 rows for now (light scan)
            print(f"✅ Successfully read: {file_path}")
            print(df.head())  # Show preview of first few rows
            # (Later: deeper ingestion like validation, feature extraction, pattern tagging)
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")

def run_ingestion():
    """Main ingestion runner."""
    print("🚀 Starting Quanta Ingestion...")
    all_files = find_all_gz_files(BASE_DIR)
    print(f"🔍 Found {len(all_files)} files to process.")

    for file_path in all_files:
        process_file(file_path)

    print("🎯 Ingestion completed.")

if __name__ == "__main__":
    run_ingestion()
