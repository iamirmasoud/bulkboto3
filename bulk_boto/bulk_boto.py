import itertools
import logging
import os
import time
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import List

import boto3
import botocore
from botocore.client import Config
from tqdm import tqdm

from bulk_boto.transfer_path import StorageTransferPath

logger = logging.getLogger(__name__)


def single_upload(input_tuple):
    s3_bucket, upload_path = input_tuple
    s3_bucket.upload_file(upload_path.local_path, upload_path.storage_path)


def single_download(input_tuple):
    s3_bucket, download_path = input_tuple
    s3_bucket.download_file(download_path.storage_path, download_path.local_path)


class BulkBoto:
    def __init__(
        self,
        endpoint_url: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        max_pool_connections: int = 300,
        verbose: bool = False,
    ) -> None:
        """
        :param endpoint_url: Endpoint_url
        :param aws_access_key_id: AWS access key id
        :param aws_secret_access_key: AWS secret access key
        :param max_pool_connections: Number of allowed pool connections
        :param verbose: Show upload progressbar.
        """
        self.verbose = verbose
        try:
            self.s3 = boto3.resource(
                "s3",
                endpoint_url=endpoint_url,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                config=Config(signature_version="s3v4", max_pool_connections=max_pool_connections),
            )
        except Exception as e:
            logger.exception(f"Cannot connect to S3. {e}")
            raise

    def create_new_bucket(self, bucket_name: str) -> None:
        """
        Create a new bucket on the object storage.
        :param bucket_name: Name of the bucket.
        """
        try:
            self.s3.create_bucket(Bucket=bucket_name)
            logger.info(f"Successfully created new bucket: '{bucket_name}'.")
        except Exception as e:
            logger.warning(f"Cannot create bucket: '{bucket_name}'. {e}")

    def empty_bucket(self, bucket_name: str) -> None:
        """
        Delete all objects of a bucket.
        :param bucket_name: Name of the bucket.
        """
        try:
            self.s3.Bucket(bucket_name).objects.all().delete()
            logger.info(f"Successfully deleted objects on: '{bucket_name}'.")
        except Exception as e:
            logger.warning(f"Cannot empty bucket: '{bucket_name}'. {e}")

    def upload(self, bucket_name: str, upload_paths: List[StorageTransferPath]) -> None:
        """
        Upload list of local files to object storage one by one.
        :param bucket_name: Name of the bucket.
        :param upload_paths: List of `StorageTransferPath` objects to upload from local to object storage.
        """
        bucket = self.s3.Bucket(bucket_name)
        for path in tqdm(upload_paths, disable=not self.verbose):
            bucket.upload_file(path.local_path, path.storage_path)

    def download(self, bucket_name: str, download_paths: List[StorageTransferPath]) -> None:
        """
        Download list of objects from object storage to local one by one.
        :param bucket_name: Name of the bucket.
        :param download_paths: List of StorageTransferPath objects to download from object storage to local.
        """
        bucket = self.s3.Bucket(bucket_name)
        for path in tqdm(download_paths, disable=not self.verbose):
            bucket.download_file(path.storage_path, path.local_path)

    def check_object_exists(
        self,
        bucket_name: str,
        object_path: str,
    ) -> bool:
        """
        Check if an object exists on the object storage.
        :param bucket_name: Name of the bucket.
        :param object_path: Path of the object to check.
        :return: True if the object exists, False otherwise.
        """
        try:
            self.s3.Object(bucket_name, object_path).load()
            return True
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            else:
                # Something else has gone wrong.
                raise

    def get_objects_list(self, bucket_name: str, storage_dir: str = "") -> List[str]:
        """
        Get all objects list in a specific on the object storage.
        :param bucket_name: Name of the bucket.
        :param storage_dir: Base directory on the object storage get list of objects.
        """
        return [s3_object.key for s3_object in self.s3.Bucket(bucket_name).objects.filter(Prefix=storage_dir)]

    def upload_dir_to_storage(self, bucket_name: str, local_dir: str, storage_dir: str, n_threads: int = 50) -> None:
        """
        Upload a local directory with its structure to the object storage.
        :param bucket_name: Name of the bucket.
        :param local_dir: Local base directory to upload objects. It must end with /.
        :param storage_dir: Object storage base directory to upload objects.
        :param n_threads: Number of threads to use. Set `n_threads` to 1 for non-parallel usage.
        """
        logger.info(
            f"Start uploading from local '{local_dir}' to '{storage_dir}' on the object storage "
            f"with {n_threads} threads."
        )

        local_files = [str(path) for path in Path(local_dir).rglob("*") if path.is_file()]
        upload_paths = []
        for local_file_path in local_files:
            s3_target_file_path = os.path.join(storage_dir, local_file_path.split(local_dir)[1])
            upload_paths.append(StorageTransferPath(storage_path=s3_target_file_path, local_path=local_file_path))

        try:
            start_time = time.time()
            # parallel operation
            if n_threads > 1:
                s3_bucket = self.s3.Bucket(bucket_name)
                with ThreadPool(n_threads) as pool:
                    list(
                        tqdm(
                            pool.imap(
                                single_upload,
                                zip(itertools.repeat(s3_bucket), upload_paths),
                            ),
                            total=len(upload_paths),
                            disable=not self.verbose,
                        )
                    )
            # serial operation
            else:
                self.upload(bucket_name, upload_paths=upload_paths)

            logger.info(
                f"Successfully uploaded {len(upload_paths)} files to '{bucket_name}' "
                f"in {(time.time() - start_time)} seconds."
            )
        except Exception as e:
            logger.exception(f"Cannot upload_parallel files. {e}")
            raise

    def download_dir_from_storage(
        self, bucket_name: str, local_dir: str, storage_dir: str, n_threads: int = 50
    ) -> None:
        """
        Download a whole directory with its structure from the object storage to a local directory.
        :param bucket_name: Name of the bucket.
        :param local_dir: Local base directory to put downloaded objects. It must end with /.
        :param storage_dir: Object storage base  directory to download objects from.
        :param n_threads: Number of threads to use. Set `n_threads` to 1 for non-parallel usage.
        """
        logger.info(f"Start downloading from '{storage_dir}' on S3 to local '{local_dir}' with {n_threads} threads.")

        s3_objects = [s3_object.key for s3_object in self.s3.Bucket(bucket_name).objects.filter(Prefix=storage_dir)]

        # Create the s3 directories structure in local
        unique_dirs = {os.path.split(path)[0] for path in s3_objects}
        for directory in unique_dirs:
            if not os.path.exists(directory):
                os.makedirs(os.path.join(local_dir, directory), exist_ok=True)

        download_paths = []
        for s3_object in s3_objects:
            download_paths.append(
                StorageTransferPath(storage_path=s3_object, local_path=os.path.join(local_dir, s3_object))
            )

        try:
            start_time = time.time()
            s3_bucket = self.s3.Bucket(bucket_name)
            if n_threads > 1:
                with ThreadPool(n_threads) as pool:
                    list(
                        tqdm(
                            pool.imap(
                                single_download,
                                zip(itertools.repeat(s3_bucket), download_paths),
                            ),
                            total=len(download_paths),
                            disable=not self.verbose,
                        )
                    )
            else:
                self.download(bucket_name, download_paths=download_paths)

            logger.info(
                f"Successfully downloaded {len(download_paths)} files from '{bucket_name}' "
                f"in {(time.time() - start_time)} seconds."
            )
        except Exception as e:
            logger.exception(f"Cannot download files. {e}")
            raise
