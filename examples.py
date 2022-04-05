import logging

from bulkboto import BulkBoto, StorageTransferPath

logging.basicConfig(
    level="INFO",
    format="%(asctime)s — %(levelname)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

TARGET_BUCKET = "test-bucket"
NUM_TRANSFER_THREADS = 50
TRANSFER_VERBOSITY = True

# instantiate a BulkBoto object
bulkboto_agent = BulkBoto(
    resource_type="s3",
    endpoint_url="<Your storage endpoint>",
    aws_access_key_id="<Your access key>",
    aws_secret_access_key="<Your secret key>",
    max_pool_connections=300,
    verbose=TRANSFER_VERBOSITY,
)

# create a new bucket
bulkboto_agent.create_new_bucket(bucket_name=TARGET_BUCKET)

# upload a whole directory with its structure to an S3 bucket in multi thread mode
bulkboto_agent.upload_dir_to_storage(
    bucket_name=TARGET_BUCKET,
    local_dir="test_dir",
    storage_dir="my_storage_dir",
    n_threads=NUM_TRANSFER_THREADS,
)

# download a whole directory with its structure to a local directory in multi thread mode
bulkboto_agent.download_dir_from_storage(
    bucket_name=TARGET_BUCKET,
    storage_dir="my_storage_dir",
    local_dir="new_test_dir",
    n_threads=NUM_TRANSFER_THREADS,
)

# upload arbitrary files to an S3 bucket
upload_paths = [
    StorageTransferPath(
        local_path="test_dir/first_subdir/f2",
        storage_path="f2",
    ),
    StorageTransferPath(
        local_path="test_dir/second_subdir/f4",
        storage_path="my_storage_dir/f4",
    ),
]
bulkboto_agent.upload(bucket_name=TARGET_BUCKET, upload_paths=upload_paths)

# download arbitrary files from an S3 bucket
download_paths = [
    StorageTransferPath(
        storage_path="f2",
        local_path="f2",
    ),
    StorageTransferPath(
        storage_path="my_storage_dir/f4",
        local_path="f5",
    ),
]
bulkboto_agent.download(bucket_name=TARGET_BUCKET, download_paths=download_paths)

# check if a file exists in a bucket
print(
    bulkboto_agent.check_object_exists(
        bucket_name=TARGET_BUCKET,
        object_path="my_storage_dir/first_subdir/test_file.txt",
    )
)
print(
    bulkboto_agent.check_object_exists(
        bucket_name=TARGET_BUCKET, object_path="my_storage_dir/first_subdir/f1"
    )
)

# get list of objects in a bucket (with prefix)
print(
    bulkboto_agent.list_objects(bucket_name=TARGET_BUCKET, storage_dir="my_storage_dir")
)
print(
    bulkboto_agent.list_objects(
        bucket_name=TARGET_BUCKET, storage_dir="my_storage_dir/second_subdir"
    )
)

# delete all objects on a bucket
bulkboto_agent.empty_bucket(TARGET_BUCKET)
