from setuptools import find_namespace_packages, setup

# Generic release markers:
#   X.Y.Z
#   X : for major change and new modelings
#   Y : for modeling enhancement
#   Z : for bug fixes and refactors
VERSION = "1.0.0"
DESCRIPTION = "Bulk Boto Package"
LONG_DESCRIPTION = "Bulk and parallel Boto package"

print(f"Installing Bulk Boto version: {VERSION}")

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
    keywords=["boto", "s3", "parallel", "bulk"],
    # TODO: add classifiers
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3.9",
    ],
)
