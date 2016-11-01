#!/usr/bin/env python

from distutils.core import setup

setup(name="flask_helpers",
      version="0.1",
      description="Useful stuff for Flask application",
      packages=["flask_helpers"],
      data_files=[("templates",
                   ["flask_helpers/templates/routing_map.html"])])
