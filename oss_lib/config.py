# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import argparse
import copy
import io
import logging
import logging.config
import os
import re

import jsonschema
import six
import yaml

LOG = logging.getLogger(__name__)

LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

_CONF = {}


class _Config(object):
    def __getitem__(self, key):
        return _CONF[key]

    def __iter__(self):
        return iter(_CONF)

    def __len__(self):
        return len(_CONF)

    def __contains__(self, key):
        return key in _CONF

    def keys(self):
        return list(_CONF)

    def values(self):
        return _CONF.values()

    def get(self, key):
        return _CONF.get(key)

CONF = _Config()


def process_args(service_prefix, parser=None,
                 default_config_path=None, defaults=None,
                 validation_schema=None):
    args = parse_args(service_prefix, parser=parser)
    setup_config(args.config_path,
                 default_config_path=default_config_path,
                 defaults=defaults,
                 log_config_path=args.log_config_path,
                 debug=args.debug,
                 validation_schema=validation_schema)
    return args


def process_env(service_prefix,
                default_config_path=None, defaults=None,
                validation_schema=None):
    variables = get_env_variables(service_prefix)
    setup_config(variables["config_path"],
                 default_config_path=default_config_path,
                 defaults=defaults,
                 log_config_path=variables["log_config_path"],
                 debug=variables["debug"],
                 validation_schema=validation_schema)


def parse_args(service_prefix, parser=None):
    check_service_prefix(service_prefix)
    if not parser:
        parser = argparse.ArgumentParser()
    register_arguments(parser, service_prefix)
    defaults = get_env_variables(service_prefix)
    parser.set_defaults(**defaults)
    args = parser.parse_args()
    return args


def check_service_prefix(service_prefix):
    if not re.match(r"^[A-Z][_A-Z0-9]*$", service_prefix):
        raise RuntimeError(
            'Incorrect service_prefix="{0}": have to start from uppercase '
            'letter and can contain uppercase letters, numbers and '
            'underscores.'.format(service_prefix))


def register_arguments(parser, service_prefix):
    parser.add_argument(
        "--config-file",
        dest="config_path",
        metavar="PATH",
        help="Path to a configuration file, overrides the {0}_CONF "
             "environment variable.".format(service_prefix),
    )
    parser.add_argument(
        "--log-config-file",
        dest="log_config_path",
        metavar="PATH",
        help="Path to a logging configuration file, overrides the "
             "{0}_LOG_CONF environment variable.".format(service_prefix),
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Set the logging level to DEBUG, overrides {0}_DEBUG "
             "environment variable. (default: false).".format(service_prefix),
    )
    return parser


def get_env_variables(service_prefix):
    debug = os.environ.get(service_prefix + "_DEBUG") == "true"
    variables = {
        "config_path": os.environ.get(service_prefix + "_CONF"),
        "log_config_path": os.environ.get(service_prefix + "_LOG_CONF"),
        "debug": debug,
    }
    return variables


def setup_config(config_path=None, default_config_path=None, defaults=None,
                 log_config_path=None, debug=False,
                 validation_schema=None):
    global CONF, _CONF

    setup_logging(log_config_path, debug=debug)

    if defaults:
        config = copy.deepcopy(defaults)
    else:
        config = {}

    loaded_config = load_config_file(config_path, default_config_path)
    if loaded_config:
        merge_dicts(config, loaded_config)

    if debug:
        log_config(config, config_path, default_config_path)

    validate_config(config, validation_schema)
    _CONF = config
    return CONF


def setup_logging(config_path, debug=False):
    if not config_path:
        logging.basicConfig(format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    else:
        LOG.info("Logging configuration file is specified: %s",
                 config_path)
        logging.config.fileConfig(config_path)
    if debug:
        LOG.info("Setting up the DEBUG logging level.")
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)


def load_config_file(config_path, default_config_path=None):
    config = None
    if config_path:
        LOG.info("Configuration file was specified: %s", config_path)
        config = yaml_load(config_path)
    elif default_config_path and os.path.exists(default_config_path):
        LOG.info("Trying to read default configuration file: %s",
                 default_config_path)
        config = yaml_load(default_config_path)
    return config


def yaml_load(path):
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except IOError as exc:
        LOG.error("Could not read content from %s: %s", path, exc)
        raise
    except yaml.YAMLError as exc:
        LOG.exception("Could not parse YAML-content from %s: %s", path, exc)
        raise


def merge_dicts(source, other):
    for key, other_value in six.iteritems(other):
        try:
            value = source[key]
        except KeyError:
            source[key] = other_value
            continue
        if (isinstance(value, dict) and
                isinstance(other_value, dict)):
            merge_dicts(value, other_value)
        else:
            source[key] = other_value


def log_config(config, config_path, default_config_path):
    LOG.debug("Configuration files: config_path=%s, default_config_path=%s",
              config_path, default_config_path)
    LOG.debug("Content of the configuration:")
    content = io.BytesIO()
    yaml.dump(config, stream=content, default_flow_style=False)
    content.seek(0)
    for line in content:
        LOG.debug(line)


def validate_config(config, validation_schema=None):
    schema = {
        "type": "object",
        "$schema": "http://json-schema.org/draft-04/schema",
        "properties": {},
        "additionalProperties": False,
    }
    # TODO(akscram): Generate the `required` key based on passed
    #                defaults and validation_schema properties.
    if validation_schema:
        schema["properties"].update(validation_schema)
    jsonschema.validate(config, schema)
