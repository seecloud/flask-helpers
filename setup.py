from setuptools import setup

setup(
    name="oss_lib",
    version="0.1.1",
    description="OSS Tooling Library",
    license="Apache 2.0",
    url="https://github.com/seecloud/oss-lib",
    author="Alexander Maretskiy",
    author_email="amaretskiy@mirantis.com",
    platforms="any",
    zip_safe=False,
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    install_requires=[
        "Flask==0.11.1", # BSD
        "PyYAML>=3.10.0", # MIT
        "jsonschema>=2.0.0,!=2.5.0,<3.0.0", # MIT
        "six>=1.9.0", # MIT
    ],
    packages=["oss_lib"],
    package_dir={"oss_lib": "oss_lib"},
    package_data={"oss_lib": ["templates/*.html"]},
)
