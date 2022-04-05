# Change Log:
**v1.0.3:**
- Add use case of transferring arbitrary files to S3

**v1.0.2:**
- Fix `find_namespace_packages` argument in `setup.py`

**v1.0.1:**
- Fix links for PyPI

**v1.0.0:**
- Initial release
- Features:
  - Multi-thread uploading/downloading of a directory (keeping the directory structure) to/from S3 object storage
  - Deleting all objects of an S3 bucket
  - Checking the existence of an object on the S3 bucket
  - Listing all objects on an S3 bucket
  - Creating a new S3 bucket on the object storage