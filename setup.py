import io
import pathlib

from setuptools import find_namespace_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# Package meta-data.
NAME = "bulkboto"
VERSION = "1.0.2"
DESCRIPTION = "A python package for parallel and bulk operations on S3 based on boto3"
URL = "https://github.com/iamirmasoud/bulkboto"
AUTHOR = "Amir Masoud Sefidian"
AUTHOR_EMAIL = "amir.masoud.sefidian@gmail.com"
REQUIRES_PYTHON = ">=3.3.0"

# What packages are required for this module to be executed?
REQUIRED = [
    "boto3==1.21.26",
    "tqdm",
]
# What packages are optional?
EXTRAS = {"dev": ["isort", "black"]}

try:
    with io.open((HERE / "README.md"), encoding="utf-8") as f:
        LONG_DESCRIPTION = "\n" + f.read()
except FileNotFoundError:
    LONG_DESCRIPTION = DESCRIPTION

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url=URL,
    license="MIT",
    python_requires=REQUIRES_PYTHON,
    packages=find_namespace_packages(include=["bulkboto"]),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    keywords=[
        "Boto3",
        "S3",
        "Parallel",
        "Bulk",
        "Boto",
        "Bulk Boto",
        "Simple Storage Service",
        "Minio",
        "Amazon AWS S3",
        "Python",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
)
