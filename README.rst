Mirantis OSS Tooling Library
============================

A library which contains various functions and classes which help to build
unified OSS Tools services.

Configuration and Logging
-------------------------

``oss_lib.config`` a module for finding configuration files, parsing them and
validating.

Location of Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

``oss_lib.config`` provides two functions, such as ``process_args`` and
``process_env``, to find a configuration file and use it as a source of
settings.

The ``process_args`` function accepts arguments from the command line at first
priority. If some of them are not specified, then suitable environment
variables are used, otherwise the default values are used.

The ``process_env`` gets environment variables, otherwise default values are
used.

Two of these functions accept the first position argument which is used as
a prefix for environment variables, e.g. if ``"CEAGLE"`` was specified, then
``CEAGLE_CONF`` will be expected as an environment variable.

The full list of supported command line arguments and environment variables:

=================  ====================  =======  =====================================
Argument           Environment variable  Default  Description
=================  ====================  =======  =====================================
--debug            <SERVICE>_DEBUG       false    Use DEBUG instead of INFO for
                                                  logging, possible values true/false.
--config-file      <SERVICE>_CONF                 Path to a YAML-configuration file.
--log-config-file  <SERVICE>_LOG_CONF             Path to a file with configuration for
                                                  `Python logging module`_
=================  ====================  =======  =====================================

.. _Python logging module: https://docs.python.org/3/library/logging.config.html#configuration-file-format

Both functions support the default location of a configuration file in case if
it was not specified through ``--config-file`` or ``<SERVICE>_CONF``.
The default location can be set using the ``default_config_path`` parameter and
it will be used only if this file exists.

The list of examples to understand priorities how a configuration file is
choosen:

================  ================  ===================  =================
--config-file     <SERVICE>_CONF    default_config_path  Result
================  ================  ===================  =================
/etc/ceagle.yaml  /etc/config.yaml  /etc/default.yaml    /etc/ceagle.yaml
<not set>         /etc/config.yaml  /etc/default.yaml    /etc/config.yaml
<not set>         <not set>         /etc/default.yaml    /etc/default.yaml
                                    (exists)
<not set>         <not set>         /etc/default.yaml    <not set>
                                    (does not exist)
================  ================  ===================  =================

Validation and Defaults
~~~~~~~~~~~~~~~~~~~~~~~

By default ``oss_lib.config`` expects that all configuration settings pass
through validation in the JSON Schema-like format.
The ``validation_schema`` parameter expects a dict which populates only
the ``properties`` parameter in the schema. For example, if your application
expects two top defined parameters in :

.. code-block:: python

      SCHEMA = {
          "elasticsearch": {
              "type": "object",
              "properties": {
                  "hosts": {
                      "type": "array",
                      "minItems": 1,
                      "uniqueItems": True,
                      "items": {
                         "type": "object",
                         "properties": {
                             "host": {"type": "string"},
                             "port": {"type": "integer"},
                         },
                         "required": ["host"],
                         "additionalProperties": False,
                      },
                  },
              },
              "required": ["hosts"],
              "additionalProperties": False,
          },
          "config": {
              "type": "object",
              "properties": {
                  "run_every_minutes": {
                      "type": "integer",
                      "minimum": 1,
                  },
              },
              "required": ["run_every_minutes"],
              "additionalProperties": False,
          },
      }

      config.process_env(...,
                         validation_schema=SCHEMA,
                         ....)

The default values for settings can be also specified through the ``defaults``
parameter, e.g.:

.. code-block:: python

      DEFAULTS = {
          "elasticsearch": {"hosts": [
              {"host": "127.0.0.1", "port": 9200},
          ]},
          "config": {"run_every_minutes": 2},
      }

      config.process_env(...,
                         validation_schema=SCHEMA,
                         defaults=DEFAULTS,
                         ....)

If defaults are specified, then they will be used as settings and
loaded settings from specified configuration files will be merged into them.
For example, if the configuration file contains:

.. code-block::

      elasticsearch:
        hosts:
          - host: 172.16.169.4
            port: 9200

The resulting config will look like that:

.. code-block:: python

      {
          "elasticsearch": {
              "hosts": [
                  {"host": "172.16.169.4", "port": 9200},
              ],
          },
          "config": {"run_every_minutes": 2},
      }

It means that only dictionary values are merged but primitives are just
replaced.

Usage Examples
~~~~~~~~~~~~~~

After initialization of configuration ``oss_lib.config`` module provides
a single tone object to interect with configuration settings. This object can
be accessed through the ``oss_lib.config.CONF`` variables in a dict-like way.

Let's take a look on the example how to initialize configuration accepting
command line arguments and environment variables ``example.py``:

.. code-block:: python

      from oss_lib import config

      SCHEMA = {
          "driver": {"enum": ["noop", "openstack"]},
      }

      DEFAULTS = {
          "driver": "noop",
      }

      config.process_args("CEAGLE",
                          default_config_path="/etc/default.yaml",
                          validation_schema=SCHEMA,
                          defaults=DEFAULTS)
      print(config.CONF["driver"])

So, after that you can run your application in various ways using:

#. The command line argument ``--config-file``:

.. code-block:: sh

      echo "driver: openstack" > /etc/ceagle.yaml
      python example.py --config-file /etc/ceagle.yaml  #-> openstack

#. The environment variable ``CEAGLE_CONF``:

.. code-block:: sh

      CEAGLE_CONF=/etc/ceagle.yaml
      echo "driver: openstack" > $CEAGLE_CONF
      python example.py #-> openstack

#. Or without any variables because the ``default_config_path`` parameter was
   specified:

.. code-block:: sh

      echo "driver: openstack" > /etc/default.yaml
      python example.py #-> openstack

#. Or even you can specify nothing because the ``defaults`` parameter was set:

.. code-block:: sh

      python example.py #-> noop


Useful Stuff for Flask
----------------------

routing.py
~~~~~~~~~~

Routing stuff like auto-generated HTML and JSON pages
with map of routes. This is useful for development
process and for exposing APIs.

Example:

.. code-block:: python

    from oss_lib import routing
    ...

    app = Flask(...)
    ...
    app.add_url_rule(...)  # add routes
    ...

    # Now add routing map pages
    app = routing.add_routing_map(app,
                                  html_uri="/api.html",
                                  json_uri="/api.json")


Now run the application and find auto-generated pages
on given URIs */api.html* and */api.json*
