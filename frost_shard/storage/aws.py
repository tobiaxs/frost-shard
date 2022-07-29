from typing import BinaryIO

import boto3

from frost_shard.domain.models import FileStorageModel
from frost_shard.settings import settings


class S3Storage:
    """AWS Simple Storage Service wrapper."""

    def __init__(self) -> None:
        self.bucket_name = settings.AWS_S3_BUCKET_NAME
        self.s3 = boto3.resource("s3")
        Bucket = getattr(self.s3, "Bucket")  # noqa: N806
        self.bucket = Bucket(self.bucket_name)
        self.client = getattr(self.s3.meta, "client")

    def upload(self, folder: str, filename: str, file: BinaryIO) -> None:
        """Upload a file to the S3.

        Args:
            folder (str): Prefix name.
            filename (str): Name of the file.
            file (BinaryIO): File to upload.
        """
        self.client.upload_fileobj(
            file,
            self.bucket_name,
            f"{folder}/{filename}",
        )

    def collect(self) -> list[FileStorageModel]:
        """Collect all files from the S3.

        Returns:
            list[FileStorageModel]: List of files.
        """
        return self.bucket.objects.all()

    def get_file_url(self, key: str) -> str:
        """Get a presigned download URL for a file.

        Args:
            key (str): Key of the file.

        Returns:
            str: Presigned download URL.
        """
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": key},
            ExpiresIn=60,
        )
