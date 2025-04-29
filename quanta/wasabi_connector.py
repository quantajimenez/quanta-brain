import os
import boto3

def list_wasabi_files():
    access_key = os.getenv('WASABI_ACCESS_KEY')
    secret_key = os.getenv('WASABI_SECRET_KEY')
    bucket_name = os.getenv('WASABI_BUCKET_NAME')
    endpoint = os.getenv('WASABI_ENDPOINT')

    if not all([access_key, secret_key, bucket_name, endpoint]):
        print("Wasabi credentials missing.")
        return []

    session = boto3.session.Session()

    s3 = session.client(
        service_name='s3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        endpoint_url=endpoint
    )

    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        file_keys = [obj['Key'] for obj in response.get('Contents', [])]
        return file_keys
    except Exception as e:
        print(f"Error connecting to Wasabi: {e}")
        return []
