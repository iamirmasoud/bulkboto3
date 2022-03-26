import logging

from bulk_boto import BulkBoto

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
bulk_boto_agent = BulkBoto(
    resource_type="s3",
    endpoint_url="<Your storage endpoint>",
    aws_access_key_id="<Your access key>",
    aws_secret_access_key="<Your secret key>",
    max_pool_connections=300,
    verbose=TRANSFER_VERBOSITY,
)

# create a new bucket
bulk_boto_agent.create_new_bucket(bucket_name=TARGET_BUCKET)

# upload a whole directory with its structure to an S3 bucket in multi thread mode
bulk_boto_agent.upload_dir_to_storage(
    bucket_name=TARGET_BUCKET,
    local_dir="test_dir",
    storage_dir="my_storage_dir",
    n_threads=NUM_TRANSFER_THREADS,
)

# download a whole directory with its structure to a local directory in multi thread mode
bulk_boto_agent.download_dir_from_storage(
    bucket_name=TARGET_BUCKET,
    storage_dir="my_storage_dir",
    local_dir="new_test_dir",
    n_threads=NUM_TRANSFER_THREADS,
)


# check if a file exists in a bucket
print(
    bulk_boto_agent.check_object_exists(
        bucket_name=TARGET_BUCKET,
        object_path="my_storage_dir/first_subdir/test_file.txt",
    )
)
print(
    bulk_boto_agent.check_object_exists(
        bucket_name=TARGET_BUCKET, object_path="my_storage_dir/first_subdir/f1"
    )
)


# get list of objects in a bucket (with prefix)
print(
    bulk_boto_agent.list_objects(
        bucket_name=TARGET_BUCKET, storage_dir="my_storage_dir"
    )
)
print(
    bulk_boto_agent.list_objects(
        bucket_name=TARGET_BUCKET, storage_dir="my_storage_dir/second_subdir"
    )
)

# delete all objects on a bucket
bulk_boto_agent.empty_bucket(TARGET_BUCKET)
