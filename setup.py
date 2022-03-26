from setuptools import find_namespace_packages, setup


def readme():
    with open("README.md") as f:
        return f.read()


VERSION = "1.0.0"
DESCRIPTION = "A python package for parallel and bulk operations on S3 based on boto3"
LONG_DESCRIPTION = readme()

setup(
    name="bulk_boto",
    version=VERSION,
    author="Amir Masoud Sefidian",
    author_email="<amir.masoud.sefidian@gmail.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/iamirmasoud/bulk_boto",
    license="LICENSE",
    packages=find_namespace_packages(include=["bulk_boto.*"]),
    install_requires=[
        "boto3==1.21.26",
        "tqdm",
    ],
    keywords=[
        "Boto3",
        "S3",
        "Parallel",
        "Bulk",
        "Boto",
        "Bulk Boto",
        "Simple Storage Service",
        "Minio",
        "Amazon S3",
        "Python",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
)
