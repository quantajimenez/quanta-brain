# background_worker.py

import boto3
import os
import gzip
import shutil
import pandas as pd
from io import BytesIO

# Wasabi config (already in Render ENV)
WASABI_ACCESS_KEY = os.getenv('WASABI_ACCESS_KEY')
WASABI_SECRET_KEY = os.getenv('WASABI_SECRET_KEY')
WASABI_ENDPOINT = 'https://s3.us-east-1.wasabisys.com'
BUCKET_NAME = 'quanta-stock-data'

# Where to temporarily store files
LOCAL_TEMP_FOLDER = '/tmp/wasabi_files'

def download_and_extract_files():
    # Create temp folder if not exist
    if not os.path.exists(LOCAL_TEMP_FOLDER):
        os.makedirs(LOCAL_TEMP_FOLDER)

    # Connect to Wasabi
    session = boto3.session.Session()
    s3 = session.client('s3',
                        endpoint_url=WASABI_ENDPOINT,
                        aws_access_key_id=WASABI_ACCESS_KEY,
                        aws_secret_access_key=WASABI_SECRET_KEY)

    # List objects
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)

    if 'Contents' not in response:
        print("\n⚠️ No files found in Wasabi bucket.")
        return

    print(f"\n✅ {len(response['Contents'])} files found. Starting download...\n")

    for obj in response['Contents']:
        key = obj['Key']
        print(f"Downloading {key}...")

        # Get file
        file_obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        file_content = file_obj['Body'].read()

        # Save compressed file temporarily
        compressed_file_path = os.path.join(LOCAL_TEMP_FOLDER, os.path.basename(key))
        with open(compressed_file_path, 'wb') as f:
            f.write(file_content)

        # Decompress on the fly
        decompressed_file_path = compressed_file_path.replace('.gz', '')
        with gzip.open(compressed_file_path, 'rb') as f_in:
            with open(decompressed_file_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        print(f"Extracted {decompressed_file_path}")

        # OPTIONAL: Load into Pandas now (this will evolve later)
        try:
            df = pd.read_csv(decompressed_file_path)
            print(f"✅ Loaded {len(df)} rows from {os.path.basename(decompressed_file_path)}")
            # TODO: feed df into Quanta brain/ML
        except Exception as e:
            print(f"⚠️ Failed to load {decompressed_file_path}: {str(e)}")

if __name__ == "__main__":
    download_and_extract_files()
