# wasabi_ingestion_test.py

import boto3
import os

# Use environment variables (you already have these in Render)
WASABI_ACCESS_KEY = os.getenv('WASABI_ACCESS_KEY')
WASABI_SECRET_KEY = os.getenv('WASABI_SECRET_KEY')
WASABI_ENDPOINT = 'https://s3.us-east-1.wasabisys.com'
BUCKET_NAME = 'quanta-stock-data'

def list_files_in_wasabi():
    session = boto3.session.Session()
    s3 = session.client('s3',
        endpoint_url=WASABI_ENDPOINT,
        aws_access_key_id=WASABI_ACCESS_KEY,
        aws_secret_access_key=WASABI_SECRET_KEY
    )

    response = s3.list_objects_v2(Bucket=BUCKET_NAME)

    if 'Contents' in response:
        print(f"\n✅ Found {len(response['Contents'])} files in Wasabi bucket '{BUCKET_NAME}':\n")
        for obj in response['Contents']:
            print(f"- {obj['Key']}")
    else:
        print("\n⚠️ No files found in the Wasabi bucket!")

if __name__ == "__main__":
    list_files_in_wasabi()
