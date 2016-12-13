Mirantis OSS Tooling Library
============================

Useful stuff for Flask
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
