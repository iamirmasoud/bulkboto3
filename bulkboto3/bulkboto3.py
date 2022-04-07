import itertools
import logging
import multiprocessing as mp
import os
import time
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import List, Union

import boto3
import botocore
from botocore.client import Config
from tqdm import tqdm

from .exceptions import DirectoryNotFoundException
from .transfer_path import StorageTransferPath

logger = logging.getLogger(__name__)


def single_upload(input_tuple):
    bucket, upload_path = input_tuple
    bucket.upload_file(upload_path.local_path, upload_path.storage_path)


def single_download(input_tuple):
    bucket, download_path = input_tuple
    bucket.download_file(download_path.storage_path, download_path.local_path)


class BulkBoto3:
    def __init__(
        self,
        endpoint_url: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        max_pool_connections: int = 300,
        resource_type: str = "s3",
        verbose: bool = False,
    ) -> None:
        """
        :param endpoint_url: Endpoint_url.
        :param aws_access_key_id: AWS access key id.
        :param aws_secret_access_key: AWS secret access key.
        :param max_pool_connections: Number of allowed pool connections.
        :param verbose: Show upload progressbar.
        """
        self.verbose = verbose
        try:
            self.resource = boto3.resource(
                resource_type,
                endpoint_url=endpoint_url,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                config=Config(
                    signature_version="s3v4",
                    max_pool_connections=max_pool_connections,
                ),
            )
        except Exception as e:
            logger.exception(f"Cannot connect to object storage. {e}")
            raise

    def _get_bucket(self, bucket_name: str):
        """
        Get a bucket object from bucket name.
        :param bucket_name: Name of the bucket.
        :return: Bucket object.
        """
        return self.resource.Bucket(bucket_name)

    def create_new_bucket(self, bucket_name: str) -> None:
        """
        Create a new bucket on the object storage.
        :param bucket_name: Name of the bucket.
        """
        try:
            self.resource.create_bucket(Bucket=bucket_name)
            logger.info(f"Successfully created new bucket: '{bucket_name}'.")
        except Exception as e:
            logger.warning(f"Cannot create a new bucket: '{bucket_name}'. {e}")

    def empty_bucket(self, bucket_name: str) -> None:
        """
        Delete all objects of a bucket.
        :param bucket_name: Name of the bucket.
        """
        try:
            bucket = self._get_bucket(bucket_name)
            bucket.objects.all().delete()
            logger.info(f"Successfully deleted objects on: '{bucket_name}'.")
        except Exception as e:
            logger.warning(f"Cannot empty bucket: '{bucket_name}'. {e}")

    def upload(
        self,
        bucket_name: str,
        upload_paths: Union[StorageTransferPath, List[StorageTransferPath]],
    ) -> None:
        """
        Upload list of local files to object storage one by one.
        :param bucket_name: Name of the bucket.
        :param upload_paths: List of `StorageTransferPath` objects to upload from local to object storage.
        """
        if isinstance(upload_paths, StorageTransferPath):
            upload_paths = [upload_paths]
        bucket = self._get_bucket(bucket_name)
        try:
            for path in tqdm(upload_paths, disable=not self.verbose):
                bucket.upload_file(path.local_path, path.storage_path)
            logger.info(
                f"Successfully uploaded {len(upload_paths)} files to bucket: '{bucket_name}'."
            )
        except Exception as e:
            logger.exception(f"Cannot upload files. {e}")
            raise

    def download(
        self,
        bucket_name: str,
        download_paths: Union[StorageTransferPath, List[StorageTransferPath]],
    ) -> None:
        """
        Download list of files from object storage to local one by one.
        :param bucket_name: Name of the bucket.
        :param download_paths: List of `StorageTransferPath` objects to download from object storage to local.
        """
        if isinstance(download_paths, StorageTransferPath):
            download_paths = [download_paths]

        bucket = self._get_bucket(bucket_name)
        try:
            for path in tqdm(download_paths, disable=not self.verbose):
                bucket.download_file(path.storage_path, path.local_path)
            logger.info(
                f"Successfully downloaded {len(download_paths)} files from bucket: '{bucket_name}'."
            )

        except Exception as e:
            logger.exception(f"Cannot download files. {e}")
            raise

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
            self.resource.Object(bucket_name, object_path).load()
            return True
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            else:
                logger.exception("Something else has gone wrong.")
                raise

    def list_objects(
        self, bucket_name: str, storage_dir: str = ""
    ) -> List[str]:
        """
        Get the list of all objects in a specific directory on the object storage.
        :param bucket_name: Name of the bucket.
        :param storage_dir: Base directory on the object storage to get list of objects.
        """
        bucket = self._get_bucket(bucket_name)
        return [
            _object.key
            for _object in bucket.objects.filter(Prefix=storage_dir)
        ]

    def upload_dir_to_storage(
        self,
        bucket_name: str,
        local_dir: str,
        storage_dir: str = "",
        n_threads: int = mp.cpu_count() * 7,
    ) -> None:
        """
        Upload a local directory with its structure (subdirectories) to the object storage.
        :param bucket_name: Name of the bucket.
        :param local_dir: Local base directory to upload objects from.
        :param storage_dir: Object storage base directory to upload objects.
        :param n_threads: Number of threads to use. Set `n_threads` to 1 for non-parallel mode.
        """
        logger.info(
            f"Start uploading from local '{local_dir}' to '{storage_dir}' on the object storage "
            f"with {n_threads} threads."
        )

        if not Path(local_dir).is_dir():
            raise DirectoryNotFoundException(
                f"Directory `{local_dir}` does not exists."
            )

        local_files = [
            str(path) for path in Path(local_dir).rglob("*") if path.is_file()
        ]
        upload_paths = []
        for local_file_path in local_files:
            storage_file_path = os.path.join(
                storage_dir, os.path.relpath(local_file_path, local_dir)
            )
            upload_paths.append(
                StorageTransferPath(
                    storage_path=storage_file_path, local_path=local_file_path
                )
            )

        if not upload_paths:
            logger.warning(f"No files found at `{local_dir}`.")
            return

        try:
            start_time = time.time()
            # parallel operation
            if n_threads > 1:
                bucket = self._get_bucket(bucket_name)
                with ThreadPool(n_threads) as pool:
                    list(
                        tqdm(
                            pool.imap(
                                single_upload,
                                zip(itertools.repeat(bucket), upload_paths),
                            ),
                            total=len(upload_paths),
                            disable=not self.verbose,
                        )
                    )
            # serial operation
            else:
                self.upload(bucket_name=bucket_name, upload_paths=upload_paths)

            logger.info(
                f"Successfully uploaded {len(upload_paths)} files to bucket '{bucket_name}' "
                f"in {(time.time() - start_time):.2f} seconds."
            )
        except Exception as e:
            logger.exception(f"Cannot upload files. {e}")
            raise

    def download_dir_from_storage(
        self,
        bucket_name: str,
        storage_dir: str,
        local_dir: str = "",
        n_threads: int = mp.cpu_count() * 7,
    ) -> None:
        """
        Download a whole directory with its structure (subdirectories) from the object storage to a local directory.
        :param bucket_name: Name of the bucket.
        :param local_dir: Local directory to put downloaded objects.
        :param storage_dir: Object storage base directory to download objects from.
        :param n_threads: Number of threads to use. Set `n_threads` to 1 for non-parallel mode.
        """
        logger.info(
            f"Start downloading from '{storage_dir}' on storage to local '{local_dir}' with {n_threads} threads."
        )
        objects = self.list_objects(
            bucket_name=bucket_name, storage_dir=storage_dir
        )

        # create the directories structure in local
        unique_dirs = {os.path.dirname(path) for path in objects}
        for directory in unique_dirs:
            if not os.path.exists(directory):
                os.makedirs(os.path.join(local_dir, directory), exist_ok=True)

        download_paths = []
        for _object in objects:
            download_paths.append(
                StorageTransferPath(
                    storage_path=_object,
                    local_path=os.path.join(local_dir, _object),
                )
            )

        if not download_paths:
            logger.warning(f"No files found at `{storage_dir}`.")
            return
        try:
            start_time = time.time()
            bucket = self._get_bucket(bucket_name)
            if n_threads > 1:
                with ThreadPool(n_threads) as pool:
                    list(
                        tqdm(
                            pool.imap(
                                single_download,
                                zip(itertools.repeat(bucket), download_paths),
                            ),
                            total=len(download_paths),
                            disable=not self.verbose,
                        )
                    )
            else:
                self.download(
                    bucket_name=bucket_name, download_paths=download_paths
                )

            logger.info(
                f"Successfully downloaded {len(download_paths)} files from bucket: '{bucket_name}' "
                f"in {(time.time() - start_time):.2f} seconds."
            )
        except Exception as e:
            logger.exception(f"Cannot download files. {e}")
            raise
