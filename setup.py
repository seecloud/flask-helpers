from setuptools import setup

setup(
    name="oss_lib",
    version="0.1.0",
    description="OSS Tooling Library",
    url="https://github.com/seecloud/oss-lib",
    author="Alexander Maretskiy",
    author_email="amaretskiy@mirantis.com",
    packages=["oss_lib"],
    package_dir={"oss_lib": "oss_lib"},
    package_data={"oss_lib": ["templates/*.html"]},
)
