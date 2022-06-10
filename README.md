<!--# Bulk Boto: Python package for fast and parallel transferring a bulk of files to S3 based on boto3-->
<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/iamirmasoud/bulkboto3">
    <img src="https://raw.githubusercontent.com/iamirmasoud/bulkboto3/main/imgs/logo.png" alt="Logo" width="100" height="100">
  </a>
    
  <h3 align="center">Bulk Boto3 (bulkboto3)</h3>

  <p align="center">
    Python package for fast and parallel transferring a bulk of files to S3 based on boto3!
    <br />
    <!-- 
    <a href="https://github.com/iamirmasoud/bulkboto3"><strong>Explore the docs »</strong></a>
    <br /> 
    -->
    <a href="https://pypi.org/project/bulkboto3/">See on PyPI</a>
    ·
    <a href="https://github.com/iamirmasoud/bulkboto3/blob/main/examples.py">View Examples</a>
    ·
    <a href="https://github.com/iamirmasoud/bulkboto3/issues">Report Bug/Request Feature</a>
    

![Python](https://img.shields.io/pypi/pyversions/bulkboto3.svg?style=flat&https://pypi.python.org/pypi/bulkboto3/)
![Version](http://img.shields.io/pypi/v/bulkboto3.svg?style=flat&https://pypi.python.org/pypi/bulkboto3/)
![License](http://img.shields.io/pypi/l/bulkboto3.svg?style=flat&https://github.com/iamirmasoud/bulkboto3/blob/main/LICENSE)
    
</p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-bulkboto3">About bulkboto3</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#blog-posts">Blog Posts</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contributors">Contributors</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>

## About bulkboto3
[Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) is the official Python SDK 
for accessing and managing all AWS resources such as Amazon Simple Storage Service (S3). 
Generally, it's pretty ok to transfer a small number of files using Boto3. However, transferring a large number of 
small files impede performance. Although it only takes a few milliseconds per file to transfer, 
it can take up to hours to transfer hundreds of thousands, or millions, of files if you do it sequentially. 
Moreover, because Amazon S3 does not have folders/directories, managing the hierarchy of directories and files 
manually can be a bit tedious especially if there are many files located in different folders.

The `bulkboto3` package solves these issues. It speeds up transferring of many small files to Amazon AWS S3 by 
executing multiple download/upload operations in parallel by leveraging the Python multiprocessing module. 
Depending on the number of cores of your machine, Bulk Boto3 can make S3 transfers even 100X faster than sequential 
mode using traditional Boto3! Furthermore, Bulk Boto3 can keep the original folder structure of files and 
directories when transferring them. There are also some other features as follows.

### Main Functionalities
  - Multi-thread uploading/downloading of a directory (keeping the directory structure) to/from S3 object storage
  - Deleting all objects of an S3 bucket
  - Checking the existence of an object on the S3 bucket
  - Listing all objects on an S3 bucket
  - Creating a new bucket on the S3

## Getting Started
### Prerequisites
* [Python 3.6+](https://www.python.org/)
* [pip](https://pip.pypa.io/en/stable/)
* API credentials to access an S3 

**Note**:
You can deploy a free S3 server using [MinIO](https://min.io/) 
on your local machine by following the steps explained in: [Deploy Standalone MinIO using Docker Compose on Linux](http://www.sefidian.com/2022/04/08/deploy-standalone-minio-using-docker-compose/).
  
### Installation
Use the package manager [pip](https://pypi.org/project/bulkboto3/) to install `bulkboto3`.

```bash
pip install bulkboto3
```

## Usage
You can find the following scripts in [examples.py](https://github.com/iamirmasoud/bulkboto/blob/main/examples.py) and [examples.ipynb Notebook](https://github.com/iamirmasoud/bulkboto/blob/main/examples.ipynb).

#### Import and instantiate a `BulkBoto3` object with your credentials
```python
from bulkboto3 import BulkBoto3
TARGET_BUCKET = "test-bucket"
NUM_TRANSFER_THREADS = 50
TRANSFER_VERBOSITY = True

bulkboto_agent = BulkBoto3(
    resource_type="s3",
    endpoint_url="<Your storage endpoint>",
    aws_access_key_id="<Your access key>",
    aws_secret_access_key="<Your secret key>",
    max_pool_connections=300,
    verbose=TRANSFER_VERBOSITY,
)
```

#### Create a new bucket
```python
bulkboto_agent.create_new_bucket(bucket_name=TARGET_BUCKET)
```

####  Upload a whole directory with its structure to an S3 bucket in multi-thread mode
Suppose that there is a directory with the following structure on your local machine:
```console
test_dir
├── first_subdir
│   ├── f1
│   ├── f2
│   └── f3
└── second_subdir
    └── f4
```
To upload the directory (with its subdirectories) to the bucket 
under a new directory name called `my_storage_dir`, use the following command:
```python
bulkboto_agent.upload_dir_to_storage(
     bucket_name=TARGET_BUCKET,
     local_dir="test_dir",
     storage_dir="my_storage_dir",
     n_threads=NUM_TRANSFER_THREADS,
)
# output:
# 2022-03-26 18:12:40 — INFO — Start uploading from local 'test_dir' to 'my_storage_dir' on the object storage with 50 threads.
# 100%|██████████| 4/4 [00:00<00:00,  4.00s/it]
# 2022-03-26 18:12:41 — INFO — Successfully uploaded 4 files to bucket 'test-bucket' in 0.07 seconds.
```

#### Download a whole directory with its structure to a local directory in multi-thread mode
```python
bulkboto_agent.download_dir_from_storage(
    bucket_name=TARGET_BUCKET,
    storage_dir="my_storage_dir",
    local_dir="new_test_dir",
    n_threads=NUM_TRANSFER_THREADS,
)
# output: 
# 2022-03-26 18:14:08 — INFO — Start downloading from 'my_storage_dir' on storage to local 'new_test_dir' with 50 threads.
# 100%|██████████| 4/4 [00:00<00:00,  4.00it/s]
# 2022-03-26 18:14:09 — INFO — Successfully downloaded 4 files from bucket: 'test-bucket' in 0.04 seconds.
```

The structure of the downloaded directory will be as follows on the local directory:
```console
new_test_dir
└── my_storage_dir
    ├── first_subdir
    │   ├── f1
    │   ├── f2
    │   └── f3
    └── second_subdir
        └── f4
```
You can set `local_dir=''` (it is the default value) to avoid the creation of the `new_test_dir` directory. 

#### Upload/Download arbitrary files to/from an S3 bucket
To transfer a list of arbitrary files to a bucket, you should instantiate `StorageTransferPath` class 
to determine the storage (s3) and local paths, and then use `.upload()` and `.download()` methods. 
Here is an example:

```python
# upload arbitrary files from local to an S3 bucket
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
# output:
# 100%|██████████| 2/2 [00:00<00:00,  2.44it/s]
# 2022-04-05 13:40:10 — INFO — Successfully uploaded 2 files to bucket: 'test-bucket'.
```
```python
# download arbitrary files from an S3 bucket to local
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
# output:
# 100%|██████████| 2/2 [00:00<00:00,  2.44it/s]
# 2022-04-05 13:34:10 — INFO — Successfully downloaded 2 files from bucket: 'test-bucket'.
```
#### Delete all objects on a bucket
```python
bulkboto_agent.empty_bucket(TARGET_BUCKET)
# output: 
# 2022-03-26 22:23:23 — INFO — Successfully deleted objects on: 'test-bucket'.
```

#### Check if a file exists in a bucket
```python
print(
    bulkboto_agent.check_object_exists(
        bucket_name=TARGET_BUCKET, object_path="my_storage_dir/first_subdir/test_file.txt"
    )
)
# output: False 

print(
    bulkboto_agent.check_object_exists(
        bucket_name=TARGET_BUCKET, object_path="my_storage_dir/first_subdir/f1"
    )
)
# output: True
```

#### Get the list of objects in a bucket (with prefix)
```python
print(
    bulkboto_agent.list_objects(
        bucket_name=TARGET_BUCKET, storage_dir="my_storage_dir"
    )
)
# output: 
# ['my_storage_dir/first_subdir/f1', 'my_storage_dir/first_subdir/f2', 'my_storage_dir/first_subdir/f3', 'my_storage_dir/second_subdir/f4']

print(
    bulkboto_agent.list_objects(
        bucket_name=TARGET_BUCKET, storage_dir="my_storage_dir/second_subdir"
    )
)
# output: 
# ['my_storage_dir/second_subdir/f4']
```

### Benchmark
Uploaded 88800 small files (totally about 7GB) with 100 threads in 505 seconds that was about 
72X faster than the non-parallel mode.

## Blog Posts
- [BulkBoto3: Python package for fast and parallel transferring a bulk of files to S3 based on boto3!](http://www.sefidian.com/2022/03/28/bulkboto3-python-package-for-fast-and-parallel-transferring-a-bulk-of-files-to-s3-based-on-boto3/)
- [Deploy Standalone MinIO using Docker Compose on Linux](http://www.sefidian.com/2022/04/08/deploy-standalone-minio-using-docker-compose/).


## Contributing
Any contributions you make are **greatly appreciated**. If you have a suggestion that would make this better, please fork the repo and create a pull request. 
You can also simply open an issue with the tag "enhancement". To contribute to `bulkboto3`, follow these steps:

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes and commit them (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

Alternatively, see the GitHub documentation on [creating a pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request).

## Contributors
Thanks to the following people who have contributed to this project:

* [Amir Masoud Sefidian](https://sefidian.com/) 📖

## Contact
If you want to contact me you can reach me at [a.m.sefidian@gmail.com](mailto:a.m.sefidian@gmail.com).

## License
Distributed under the [MIT](https://choosealicense.com/licenses/mit/) License. See `LICENSE` for more information.



