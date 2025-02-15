from typing import BinaryIO
import boto3
from config.config import STORAGE_ENDPOINT, STORAGE_ACCESS_KEY, STORAGE_SECRET_KEY


class Buckets:
    AVIDA_STORAGE = "avida-storage"


storage = boto3.client(
    "s3",
    endpoint_url=STORAGE_ENDPOINT,
    aws_access_key_id=STORAGE_ACCESS_KEY,
    aws_secret_access_key=STORAGE_SECRET_KEY,
)

resources = boto3.resource(
    "s3",
    endpoint_url=STORAGE_ENDPOINT,
    aws_access_key_id=STORAGE_ACCESS_KEY,
    aws_secret_access_key=STORAGE_SECRET_KEY,
)


def create_directory(bucket_name: str, path: str):
    try:
        storage.put_object(Bucket=bucket_name, Key=path)
    except Exception as ex:
        print(ex)
        return False
    else:
        return True


def upload_file(file: BinaryIO, bucket_name: str, path: str):
    try:
        storage.upload_fileobj(
            file,
            Bucket=bucket_name,
            Key=path
        )
    except Exception as ex:
        print(ex)
        return False
    else:
        return True


def get_bucket(bucket_name: str):
    return resources.Bucket(bucket_name)


def storage_delete_folder(path: str, bucket_name: str):
    get_bucket(bucket_name).objects.filter(Prefix=path).delete()


def storage_delete_file(path: str, bucket_name: str) -> bool:
    try:

        storage.head_object(Bucket=bucket_name, Key=path)
        storage.delete_object(Bucket=bucket_name, Key=path)
    except Exception as ex:
        print(ex)
        print('/////////////')
        return False
    else:
        print(path)
        print(bucket_name)
        return True
