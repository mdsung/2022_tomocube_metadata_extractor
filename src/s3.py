import os
from abc import ABC
from dataclasses import dataclass

import boto3
from dotenv import load_dotenv

load_dotenv()
AWS_KEY = os.getenv("AWS_KEY")
AWS_PASSWORD = os.getenv("AWS_PASSWORD")


@dataclass
class S3Credential:
    key: str
    password: str

    def __post_init__(self):
        self.key = self.key.strip()
        self.password = self.password.strip()


def get_s3_resource(credential: S3Credential):
    return boto3.resource(
        "s3",
        aws_access_key_id=credential.key,
        aws_secret_access_key=credential.password,
    )


def get_s3_bucket(credential: S3Credential, bucket_name: str):
    return get_s3_resource(credential).Bucket(bucket_name)


class S3Reader(ABC):
    def __init__(self, bucket):
        self.bucket = bucket


class S3FolderReader(S3Reader):
    def read(self) -> list[str]:
        result = self.bucket.meta.client.list_objects(
            Bucket=self.bucket.name, Delimiter="/"
        )
        return [
            obj.get("Prefix").replace("/", "")
            for obj in result.get("CommonPrefixes")
        ]


class S3FileReader(S3Reader):
    def read(self, folder_name) -> list[str]:
        if not folder_name.endswith("/"):
            folder_name += "/"

        return [
            obj.key.replace(folder_name, "")
            for obj in self.bucket.objects.filter(Prefix=folder_name)
        ]


def main():
    # s3.ObjectSummary(bucket_name='2022-tomocube-igra', key='20220707/20220707.174819.594.CD4-044_RI Tomogram.tiff')
    project_name = "2022_tomocube_igra"
    credential = S3Credential(AWS_KEY, AWS_PASSWORD)
    resource = get_s3_resource(credential)
    bucket_list = [bucket.name for bucket in resource.buckets.all()]
    # bucket = get_s3_bucket(credential, project_name.replace("_", "-"))
    # folder_reader = S3FolderReader(bucket)
    # folder_list = folder_reader.read()
    # print(folder_list)


if __name__ == "__main__":
    main()
