# Bulk Boto: Bulk and Parallel Boto



## Changes Log:

**v1.0.0:**
- A function that gets s3 bucket object list is added.
- Add `check_object_exists` method to S3Handler class. 
- Enrich `S3Handler` class utilities: 
  -  Support of parallel upload/download of a whole local directory to/from S3.
  -  Support deleting all objects of an S3 bucket.
