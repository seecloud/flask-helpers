#!/usr/bin/env python

from distutils.core import setup

setup(name="flask_helpers",
      version="0.1",
      description="Useful stuff for Flask application",
      url="https://github.com/seecloud/flask-helpers",
      author="Alexander Maretskiy",
      author_email="amaretskiy@mirantis.com",
      packages=["flask_helpers"],
      package_dir={"flask_helpers": "flask_helpers"},
      package_data={"flask_helpers": ["templates/*.html"]})
