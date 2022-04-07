import io
import os
import pathlib
import re

from setuptools import find_namespace_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# Package meta-data.
NAME = "bulkboto3"
DESCRIPTION = "Python package for fast and parallel transferring a bulk of files to S3 based on boto3"
URL = "https://github.com/iamirmasoud/bulkboto3"
AUTHOR = "Amir Masoud Sefidian"
AUTHOR_EMAIL = "amir.masoud.sefidian@gmail.com"
REQUIRES_PYTHON = ">=3.6.0"
# What packages are required for this module to be executed?
REQUIRED = [
    "boto3==1.21.26",
    "tqdm",
]

# What packages are optional?
EXTRAS = {"dev": ["isort", "black"]}


def get_version():
    init = open(os.path.join(HERE, NAME, "__init__.py")).read()
    return (
        re.compile(r"""__version__ = ['"]([0-9.]+)['"]""")
        .search(init)
        .group(1)
    )


VERSION = get_version()


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
    packages=find_namespace_packages(include=["bulkboto3"]),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    keywords=[
        "Boto3",
        "S3",
        "Parallel",
        "Multi-thread",
        "Bulk",
        "Boto",
        "Bulk Boto",
        "Bulk Boto3",
        "Simple Storage Service",
        "Minio",
        "Amazon AWS S3",
        "Python",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
)
